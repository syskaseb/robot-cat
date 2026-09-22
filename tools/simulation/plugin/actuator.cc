// Screening actuator, NOT an identified ST3215 electronics/thermal model.
// Physical effort commands only. Reads q/dq; no position or velocity reset.
#include <algorithm>
#include <cmath>
#include <mutex>
#include <vector>
#include <string>
#include <gz/plugin/Register.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/JointPosition.hh>
#include <gz/sim/components/JointVelocity.hh>
#include <gz/sim/components/JointForceCmd.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/actuators.pb.h>
#include <gz/msgs/model.pb.h>

namespace robot_cat {
class Actuator final: public gz::sim::System,
    public gz::sim::ISystemConfigure, public gz::sim::ISystemPreUpdate {
  gz::transport::Node node;
  gz::transport::Node::Publisher pub;
  std::mutex mutex;
  std::vector<std::string> names;
  std::vector<gz::sim::Entity> joints;
  std::vector<double> target;
  std::vector<double> damping;
  double stall=2.574245625, speed=4.127467826, cap=1., kp=30., kd=.5;
  double lastPublish=-1.;
 public:
  void Configure(const gz::sim::Entity &entity,
      const std::shared_ptr<const sdf::Element> &sdf,
      gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
    gz::sim::Model model(entity);
    cap=sdf->Get<double>("effort_cap",cap).first;
    stall=sdf->Get<double>("stall_torque",stall).first;
    speed=sdf->Get<double>("no_load_speed",speed).first;
    kp=sdf->Get<double>("p_gain",kp).first;
    kd=sdf->Get<double>("d_gain",kd).first;
    if(sdf->HasElement("joint_name")) {
      auto element=sdf->FindElement("joint_name");
      while(element) {
        const auto name=element->Get<std::string>();
        const auto joint=model.JointByName(ecm,name);
        if(joint==gz::sim::kNullEntity) throw std::runtime_error("Missing joint "+name);
        names.push_back(name);joints.push_back(joint);target.push_back(0);
        damping.push_back(sdf->Get<double>(name+"_d_gain",kd).first);
        if(!ecm.Component<gz::sim::components::JointPosition>(joint))
          ecm.CreateComponent(joint,gz::sim::components::JointPosition());
        if(!ecm.Component<gz::sim::components::JointVelocity>(joint))
          ecm.CreateComponent(joint,gz::sim::components::JointVelocity());
        element=element->GetNextElement("joint_name");
      }
    }
    if(joints.size()!=12) throw std::runtime_error("Expected 12 leg joints");
    node.Subscribe("/robot_cat_cad/targets",&Actuator::OnTarget,this);
    pub=node.Advertise<gz::msgs::Model>("/robot_cat_cad/actuator_state");
  }
  void OnTarget(const gz::msgs::Actuators &msg) {
    if(msg.position_size()!=static_cast<int>(joints.size()))return;
    std::lock_guard<std::mutex> lock(mutex);
    for(size_t i=0;i<joints.size();++i)
      if(!std::isfinite(msg.position(i)) || std::abs(msg.position(i))>.5)return;
    for(size_t i=0;i<joints.size();++i)target[i]=msg.position(i);
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,
                 gz::sim::EntityComponentManager &ecm) override {
    if(info.paused)return;
    const double seconds=std::chrono::duration<double>(info.simTime).count();
    const bool publish=seconds-lastPublish>=.01-1e-9;
    gz::msgs::Model state;
    state.set_name("commanded_motor_torque_not_reaction_sensor");
    state.mutable_header()->mutable_stamp()->set_sec(static_cast<int64_t>(seconds));
    state.mutable_header()->mutable_stamp()->set_nsec(static_cast<int>((seconds-std::floor(seconds))*1e9));
    std::lock_guard<std::mutex> lock(mutex);
    for(size_t i=0;i<joints.size();++i) {
      auto pos=ecm.Component<gz::sim::components::JointPosition>(joints[i]);
      auto vel=ecm.Component<gz::sim::components::JointVelocity>(joints[i]);
      if(!pos || !vel || pos->Data().empty() || vel->Data().empty())continue;
      const double q=pos->Data()[0],dq=vel->Data()[0];
      // Conservative symmetric envelope: also reduces braking above base speed.
      const double available=std::min(cap,stall*std::max(0.,1.-std::abs(dq)/speed));
      const double torque=std::clamp(kp*(target[i]-q)-damping[i]*dq,-available,available);
      auto cmd=ecm.Component<gz::sim::components::JointForceCmd>(joints[i]);
      if(cmd)cmd->Data()={torque};
      else ecm.CreateComponent(joints[i],gz::sim::components::JointForceCmd({torque}));
      if(publish) {
        auto j=state.add_joint();j->set_name(names[i]);
        j->mutable_axis1()->set_position(q);j->mutable_axis1()->set_velocity(dq);
        j->mutable_axis1()->set_force(torque);
      }
    }
    if(publish && state.joint_size()==static_cast<int>(joints.size())) {
      pub.Publish(state);lastPublish=seconds;
    }
  }
};
}
GZ_ADD_PLUGIN(robot_cat::Actuator,gz::sim::System,
    robot_cat::Actuator::ISystemConfigure,robot_cat::Actuator::ISystemPreUpdate)
GZ_ADD_PLUGIN_ALIAS(robot_cat::Actuator,"robot_cat::Actuator")
