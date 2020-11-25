"""The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameInstruction, GameStatus, PlatformAction
)

def ml_loop():
    """The main loop of the machine learning process
    This loop is run in a separate process, and communicates with the game process.
    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    aid = 0
    past_ball_position = []
    ball_down = False

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        now_ball_position = scene_info.ball
        if len(past_ball_position) == 0:
            past_ball_position = now_ball_position
        else:
            if (now_ball_position[1] - past_ball_position[1]) > 0:
                ball_down = True
            else:
                ball_down = False
        
        now_platform_positionX = scene_info.platform[0] + 20

        if ball_down == True and now_ball_position[1] > 200:
            m = (now_ball_position[1] - past_ball_position[1]) / (now_ball_position[0] - past_ball_position[0])
            aid = now_ball_position[0] - ((now_ball_position[1] - 395) / m)
            if aid < 0:
                aid = -aid
            elif aid > 200:
                aid = 200 - (aid - 200)
        else:
            aid = 100

        if aid > now_platform_positionX:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
        if aid < now_platform_positionX:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
        if aid == now_platform_positionX:
            comm.send_instruction(scene_info.frame, PlatformAction.NONE)

        past_ball_position = now_ball_position
