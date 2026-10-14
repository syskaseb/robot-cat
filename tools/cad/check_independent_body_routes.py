"""Full-scene exact gate for received independent body candidates, not W5."""
import check_body_fanout_material as C
import whole_current_body_material as M

if __name__ == '__main__':
    C.run(material_loader=M.load, report_name='independent-body-routes-material.json')
