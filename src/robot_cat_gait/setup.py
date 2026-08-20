from setuptools import find_packages, setup

package_name = "robot_cat_gait"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Sebastian Syska",
    maintainer_email="syskas01@stepstone.com",
    description="Trot gait generator for the robot cat.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "gait_controller = robot_cat_gait.gait_controller:main",
        ],
    },
)
