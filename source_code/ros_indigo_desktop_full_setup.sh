#Setup your sources.list
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

# Set up your keys
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116

#Use the apt tool to install the ros-desktop-full edition
sudo apt-get install ros-indigo-desktop-full

#Update the cash
apt-cache search ros-indigo

# Before you can use ROS, you will need to initialize rosdep. rosdep #  enables you to easily install system dependencies for source you 
#  want to compile and is required to run some core components in 
#  ROS.
sudo rosdep init
rosdep update

# Environment setup
# It's convenient if the ROS environment variables are automatically
#  added to your bash session every time a new shell is launched
echo "source /opt/ros/indigo/setup.bash" >> ~/.bashrc
source ~/.bashrc

# rosinstall is a frequently used command-line tool in ROS that is 
#  distributed separately. It enables you to easily download many 
#  source trees for ROS packages with one command.
sudo apt-get install python-rosinstall
