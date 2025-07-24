# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is all-in-one launch script intended for use by nav2 developers."""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, FindExecutable
from launch.substitutions import LaunchConfiguration, TextSubstitution
import sys
from launch.event_handlers import OnExecutionComplete, OnProcessStart
from nav2_common.launch import RewrittenYaml

# Get TPCAP_AMR path
# file_path = os.path.dirname(os.path.abspath(__file__)) + '/../'
# file_path = os.path.abspath(file_path)
# # Add New_TPCAP_AMRAMR to Python path for import config
# sys.path.append(file_path)
# import config.launch_const as const

def generate_launch_description():
    # Parameters
    namespace = LaunchConfiguration('namespace')
    params_file = LaunchConfiguration('params_file')
    # keepout_yaml = LaunchConfiguration('keepout_yaml')
    remapping_tf = LaunchConfiguration('remapping_tf')
    remapping_tf_static = LaunchConfiguration('remapping_tf_static')
    use_pose_memory = LaunchConfiguration('use_pose_memory')
    use_weight_check = LaunchConfiguration('use_weight_check')
    use_server_loop = LaunchConfiguration('use_server_loop')

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Top-level namespace')
    
    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value='',
        description='Full path to the ROS2 parameters file to use')

    declare_remapping_tf_cmd = DeclareLaunchArgument(
        'remapping_tf',
        default_value='',
        description='Remap tf to namespaced tf')

    declare_remapping_tf_static_cmd = DeclareLaunchArgument(
        'remapping_tf_static',
        default_value='',
        description='Remap tf_static to namespaced tf_static')

    declare_use_pose_memory_cmd = DeclareLaunchArgument(
        'use_pose_memory',
        default_value='true',
        description='Use pose memory node')
    
    # declare_keepout_yaml_cmd = DeclareLaunchArgument(
    #     'keepout_yaml',
    #     default_value='',
    #     description='Full path of keepout yaml file')

    declare_use_weight_check_cmd = DeclareLaunchArgument(
            'use_weight_check',
            default_value='true',
            description='Use weight check node')
    
    declare_use_server_loop_cmd = DeclareLaunchArgument(
            'use_server_loop',
            default_value='true',
            description='Use server loop node')

    remappings = [
        ('/tf', remapping_tf),  # Remap /tf topic
        ('/tf_static', remapping_tf_static),  # Remap /tf_static topic
    ]

    # Create our own temporary YAML files that include substitutions
    param_substitutions = {}

    configured_params = RewrittenYaml(
            source_file=params_file,
            root_key=namespace,
            param_rewrites=param_substitutions,
            convert_types=True)

    # Specify the actions
    state_control_cmd = Node(
        package='amr_state_operation',
        executable='state_control',
        # Name make duplicate node name when state_control create the child node
        # name='state_control',
        namespace=namespace,
        output='log',
        parameters=[configured_params])
    
    amr_service_cmd = Node(
        package='amr_state_operation',
        executable='amr_service',
        name='amr_service',
        namespace=namespace,
        output='log',
        parameters=[configured_params])

    pose_memory_cmd = Node(
        condition=IfCondition(use_pose_memory),
        package='amr_state_operation',
        executable='pose_memory',
        name='pose_memory',
        namespace=namespace,
        remappings=remappings,
        output='log',
        parameters=[configured_params])

    speed_limit_cmd = Node(
        package='amr_state_operation',
        executable='speed_limit',
        name='speed_limit',
        namespace=namespace,
        output='log',
        parameters=[configured_params])

    weight_checker_cmd = Node(
        condition=IfCondition(use_weight_check),
        package='amr_state_operation',
        executable='weight_checker',
        name='weight_checker',
        namespace=namespace,
        output='log',
        parameters=[configured_params])
    
    server_loop_cmd = Node(
        condition=IfCondition(use_server_loop),
        package='amr_state_operation',
        executable='server_loop',
        name='server_loop',
        namespace=namespace,
        output='log'
        )
    
    # autofeed_cmd = Node(
    #     package='guiding_system',
    #     executable='autofeed',
    #     name='autofeed',
    #     namespace=namespace,
    #     output='log'
    # )
    # log_wifi_strength_cmd = Node(
    #     package='amr_state_operation',
    #     executable='log_wifi_strength',
    #     name='log_wifi_strength',
    #     namespace=const.SL_NAMESPACE,
    #     output='screen',
    #     parameters=[{'hz': (const.HZ_WIFI_STRENGTH),
    #                  'path':  (const.AMR_LOG_PATH)}]
    #     )
    
    # Moved here to confirm start after state control
    # State control need keepout to judge when amr lost
    # costmap_filter_dir = get_package_share_directory('amr_costmap_filter')
    # costmap_filter_launch_dir = os.path.join(costmap_filter_dir, 'launch')
    # keepout_launch_cmd = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(costmap_filter_launch_dir, 'keepout_launch.py')),
    #     launch_arguments={'namespace': namespace,
    #     'params_file': params_file,
    #     'mask': keepout_yaml,
    #     'use_sim_time': use_sim_time}.items())
    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_use_pose_memory_cmd)
    ld.add_action(declare_use_weight_check_cmd)
    ld.add_action(declare_use_server_loop_cmd)


    # Add any conditioned actions
    # if const.KEEPOUT == 1:
    #     ld.add_action(RegisterEventHandler(
    #         event_handler=OnProcessStart(
    #             target_action=state_control_cmd,
    #             on_start=[TimerAction(period=3.0, actions=[keepout_launch_cmd])]
    #         )
    #     ))
    ld.add_action(state_control_cmd)
    ld.add_action(amr_service_cmd)
    ld.add_action(pose_memory_cmd)
    ld.add_action(speed_limit_cmd)
    ld.add_action(weight_checker_cmd)
    # ld.add_action(log_wifi_strength_cmd)
    ld.add_action(server_loop_cmd)
    ld.add_action(weight_checker_cmd)
    ld.add_action(server_loop_cmd)


    return ld