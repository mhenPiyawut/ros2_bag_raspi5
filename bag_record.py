import os
import shutil
import time
from datetime import datetime
import subprocess
import signal
# Configuration
RECORD_INTERVAL = 10*60  # 10 minutes in seconds
MAX_STORAGE_GB = 30
BAG_DIRECTORY = "./bag_files"
NAMESPACE = "amr7"  # Default namespace; adjust as needed

# Topics to record (with namespace as a placeholder)
# TOPICS = [
#     "/{ns}/odom",
#     "/{ns}/hw_input",
#     "/{ns}/cmd_vel",
#     "/{ns}/mot_gain",
#     "/{ns}/wheel_speed",
#     "/{ns}/motor_control_mode",
#     "/{ns}/motor_info",
#     "/{ns}/motor_status",
#     "/{ns}/amcl_pose",
#     "/{ns}/state_control",
#     "/{ns}/speed_limit",
#     "/{ns}/lidar_area",
#     "/{ns}/book_request_waypoint",
#     "/{ns}/speed_limit_zone_dynamic",
#     "/{ns}/cmd_vel_acc",
#     "/{ns}/acc_follow_id",
# ]
TOPICS = [
    "/{ns}/motor_states",
    "/{ns}/lidar_area",
    "/{ns}/current_node",
    "/{ns}/lookahead_point",
    "/{ns}/scan",
    "/{ns}/diagnosis_code",
    "/{ns}/mot_gain",
    "/{ns}/hw_input",
    "/{ns}/cmd_vel",
    "/{ns}/amcl_pose",
    "/{ns}/odom",
    "/{ns}/speed_limit",
    "/{ns}/route_command",
    "/{ns}/state_control",
    "/{ns}/clicked_point",
    "/{ns}/downsampled_costmap",
    "/{ns}/downsampled_costmap_updates",
    "/{ns}/global_costmap/costmap",
    "/{ns}/global_costmap/costmap_updates",
    "/{ns}/global_costmap/voxel_marked_cloud",
    "/{ns}/initialpose",
    "/{ns}/local_costmap/costmap",
    "/{ns}/local_costmap/costmap_updates",
    "/{ns}/local_costmap/published_footprint",
    "/{ns}/local_costmap/voxel_marked_cloud",
    "/{ns}/local_plan",
    "/{ns}/map",
    "/{ns}/map_updates",
    "/{ns}/parameter_events",
    "/{ns}/particle_cloud",
    "/{ns}/plan",
    "/{ns}/polygon_stop",
    "/{ns}/rosout",
    "/{ns}/speed_limit_filter_mask",
    "/{ns}/speed_limit_filter_mask_updates",
    "/{ns}/tf",
    "/{ns}/tf_static",
    "/{ns}/waypoints",
    "/{ns}/clock",
]

def get_total_size_gb(directory):
    """Calculate total size of files in a directory (in GB)."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 ** 3)  # Convert bytes to GB

def delete_oldest_bag(directory):
    """Delete the oldest bag directory."""
    bags = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    if bags:
        oldest_bag = min(bags, key=os.path.getctime)
        shutil.rmtree(oldest_bag)
        print(f"Deleted oldest bag: {oldest_bag}")

def record_rosbag(namespace, duration_sec):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(BAG_DIRECTORY, exist_ok=True)
    bag_path = os.path.join(BAG_DIRECTORY, timestamp)

    topics = " ".join([topic.format(ns=namespace) for topic in TOPICS])

    print(f"Starting recording: {bag_path}")
    command = f"ros2 bag record -o {bag_path} --include-hidden-topics -a"

    # Start ros2 bag as subprocess
    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid,
                            stdin=subprocess.DEVNULL)


    try:
        time.sleep(duration_sec)
        # Send SIGINT to entire process group to simulate Ctrl+C
        os.killpg(os.getpgid(process.pid), signal.SIGINT)
        process.wait()
        print(f"Recording stopped: {bag_path}")
    except Exception as e:
        print(f"Error during recording: {e}")
        process.kill() 

def main():
    """Main function to manage recording and storage."""
    # os.makedirs(BAG_DIRECTORY, exist_ok=True)
    while True:
        print(f"Bag folder size {get_total_size_gb(BAG_DIRECTORY)} Max {MAX_STORAGE_GB}")
        try:
            record_rosbag(NAMESPACE, RECORD_INTERVAL)
        except Exception as e:
            print(f"Error during recording: {e}")
        while get_total_size_gb(BAG_DIRECTORY) > MAX_STORAGE_GB:
            print("Storage limit exceeded. Deleting oldest bag...")
            delete_oldest_bag(BAG_DIRECTORY)

if __name__ == "__main__":
    main()