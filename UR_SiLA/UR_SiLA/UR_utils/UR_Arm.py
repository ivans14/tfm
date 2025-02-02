from typing import Tuple
import numpy as np
import yaml
import time
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
from dashboard_client import DashboardClient
from .labware import *

from .UR_Arm_Abs import URRobotAbs

##useful poses

HOME_POSE = np.array([-0.15285, -0.25362, 0.33395, 2.404, 2.420, -2.432])

SYR_DECAP_POSE = np.array([-0.2024, -0.35907, 0.1809, 0, -1.53, 0])

PEN_DECAP_POSE = np.array([-0.22329, -0.3734, 0.21731, 2.377, 2.420, -2.382])

## status

IDLE = 0
MOVING = 1
GRIPPING = 2
POURING = 3
DISCONNECTED = 4

class UR_Robot(URRobotAbs):
    def __init__(self, host: any, ) -> None:
        ##connection parameters
        self.TCP_IP = host

        self.home_pose = HOME_POSE
        self.status = DISCONNECTED
        self.vel_c = 0.1
    
    def configure_robot_params(self, syr_samp: int, syr_batch: int, Lpen_samp: int,
                  Lpen_batch: int,Spen_samp: int, Spen_batch: int):
        if syr_samp < 0 or syr_samp > 6 or Lpen_samp <0 or Lpen_samp > 6:
            return False
        self.LTray = LTray(syr_samp, syr_batch, Lpen_samp, Lpen_batch)
        self.STray = STray(Spen_samp, Spen_batch)
        self.OutTray = Out_tray(syr_batch, Lpen_samp, Lpen_batch)
        self.Lmat = self.LTray.create_matrix()
        self.Smat = self.STray.create_matrix()
        self.Outmat = self.OutTray.create_matrix()
        print(self.Lmat)
        print(self.Smat)
        print(self.Outmat)
        return True
        

    def connect(self):
        """connect to robot and initialize dashboard and receiver"""
        self.connection = RTDEControl(self.TCP_IP)
        self.receive = RTDEReceive(self.TCP_IP)
        self.dashboard = DashboardClient(hostname=self.TCP_IP)
        self.dashboard.connect()
        self.dashboard.powerOn()  
        self.dashboard.brakeRelease() 
        self.status = IDLE
        return "connection succesfull" if self.connection.isConnected() else "connection failed"
    
    def check_connection(self):
        return self.connection.isConnected()
    
    def robot_status(self):
        return self.status
    
    def check_AND_moveJ(self, pose: np.array, cartesian: bool = False):
        """ Check if pose if within safety limits and move in JointSpace. """
        # if cartesian:
        #     if self.rtde_c.isPoseWithinSafetyLimits(pose):
        #         pose = self.rtde_c.getInverseKinematics(pose)
        #     else:
        #         return False

        # if self.rtde_c.isJointsWithinSafetyLimits(pose):
        #     self.rtde_c.moveJ(pose, self.vel_q, self.acc_q)
        #     return True
        # else:
        #     return False
        print("movej to pose:",pose)

    def check_AND_moveL(self, pose: np.array, joint: bool = False):
        """ Check if pose if within safety limits and move in LinearSpace. """
        if joint:
            if self.connection.isJointsWithinSafetyLimits(pose):
                pose = self.connection.getInverseKinematics(pose)
            else:
                return False 
           
        if self.connection.isPoseWithinSafetyLimits(pose):
            self.connection.moveL(pose, self.vel_c)
            return True
        else:
            return False
        # print("movel to pose:",pose)

    
    def go_home(self):
        """Move arm to home position"""
        self.check_AND_moveL(self.home_pose)

    def select_n_play(self, program: str):
        """laod and play program"""
        self.dashboard.loadURP(program)
        self.dashboard.play()
        print(f"[INFO]: Executing {program}. ")
        self.dashboard.stop()
        self.connection.reuploadScript()
        time.sleep(0.1)

    def grip_syringe(self):
        # program = "grip_syringe.urp"
        # self.select_n_play(program)
        print("gripping syringe")


    def grip_pen(self):
        # program = "grip_pen.urp"
        # self.select_n_play(program)   
        print("gripping pen")

    # def move_to_syr_index(self, row, col):
    #     pos = Ltray_poses[row,col]

    def move_to_decapper(self, object):
        if isinstance(object, Syringe):
            self.check_AND_moveL(SYR_DECAP_POSE)
        else:
            self.check_AND_moveL(PEN_DECAP_POSE)

    ##looping programs 
    def turn_wrist(self, turned: bool, pos: list):
        if turned:
            turn = np.pi/2
            curr = self.connection.getInverseKinematics(pos)
            curr[-1] -= turn
            self.connection.moveJ(curr)
            return True
        else:
            turn = np.pi/2
            curr = self.connection.getInverseKinematics(pos)
            curr[-1] += turn
            self.connection.moveJ(curr)
            return True



    def Ltray_loop(self):
        ##find actual values
        turned = False
        initial_target = np.array([0.18865, -0.28095, 0.12454, 0.48, 2.377, -2.382])
        targetL = initial_target.copy()
        offset_moveL = np.array([0,-0.02,0,0,0,0])
        self.check_AND_moveL(targetL)
        for i in range(len(self.Lmat)):
            targetX = initial_target.copy()
            targetX[0] -= self.LTray.sep_y * i
            targetY = targetX.copy()
            print(targetX)
            time.sleep(0.1)
            for j in range(len(self.Lmat[i])):
                if self.Lmat[i][j] is not None:
                    print(i,j)
                    self.check_AND_moveL(targetX)
                    time.sleep(0.5)
                    targetY[1] -= self.LTray.sep_x
                    if isinstance(self.Lmat[i][j], Syringe):
                        self.turn_wrist(turned, targetY)
                        self.check_AND_moveL(targetY+offset_moveL)
                        turned = True
                        self.grip_syringe() 
                        self.move_to_decapper(self.Lmat[i][j])
                    else:
                        self.turn_wrist(turned, targetY)
                        turned = False
                        self.check_AND_moveL(targetY+offset_moveL)
                        self.grip_pen()
                        self.move_to_decapper(self.Lmat[i][j])
                    time.sleep(1)
                else:
                    pass
        return True
                
    def Stray_loop(self):
        ##find actual values
        initial_target = np.array([0,1,0.2,0,0,0])
        targetJ = initial_target
        offset_moveL = np.array([0,-0.2,0,0,0,0])
        self.check_AND_moveJ(targetJ)
        for i in range(len(self.Smat)):
            targetJ[0] = initial_target[0]
            targetJ[1] -= self.STray.sep_y * i
            for j in range(len(self.Smat[i])):
                if self.Smat[i][j] is not None:
                    targetJ[0] += self.STray.sep_x * j
                    self.check_AND_moveJ(targetJ)
                    self.check_AND_moveL(targetJ+offset_moveL)
                    self.grip_pen()
                else:
                    pass
        

# test = UR_Robot("1", 2, 6, 2, 4, 3, 2, 2)
# print(test.Lmat)
# test.Ltray_loop()
# print("starting stray")
# test.Stray_loop()
