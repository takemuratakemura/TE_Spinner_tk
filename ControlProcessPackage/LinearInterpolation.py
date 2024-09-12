#変数valueに対してmapで定義された点を線形補間する
#範囲の外側は最小値または最大値が入る

def linear_interpolation(target_map, value):
    """
    Performs linear interpolation based on a set of points.
    If the value is outside the range, it returns the min or max value.

    Parameters:
    points (dict): A dictionary where the keys are the input points and the values are the corresponding output points.
    value (float): The input value to interpolate.

    Returns:
    float: The interpolated output value.
    """
    # ソートされたリストに変換
    sorted_points = sorted(target_map.items())

    # 入力値が範囲外の場合、最小値または最大値を返す
    if value <= sorted_points[0][0]:
        return sorted_points[0][1]
    elif value >= sorted_points[-1][0]:
        return sorted_points[-1][1]

    # 2つの近い点を探す
    for i in range(len(sorted_points) - 1):
        x1, y1 = sorted_points[i]
        x2, y2 = sorted_points[i + 1]

        if x1 <= value <= x2:
            # 線形補間の計算
            t = (value - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)

    # ここには到達しないはず
    return None

# 操作量から目標速度引き当て
def get_target_speed(value):
    MAX_FORWARD_SPEED = 4.0 #[km/h]
    MAX_BACKWARD_SPEED = -1.0 #[km/h]

    target_speed_map = {
        -1: MAX_BACKWARD_SPEED,
        -0.9: MAX_BACKWARD_SPEED,
        -0.1: 0,
        0.1: 0,
        0.9: MAX_FORWARD_SPEED,
        1: MAX_FORWARD_SPEED
    }
    
    return linear_interpolation(target_speed_map, value)

# 速度差分から加速度引き当て
def get_target_accel(value):
    MAX_ACCEL = 0.3 #[m/s^2]

    target_accel_map = {
        0: 0,
        5: MAX_ACCEL
    }
    
    return linear_interpolation(target_accel_map, value)

# 速度差分から減速度引き当て
def get_target_decel(value):
    MAX_DECEL = -1.4 #[m/s^2]

    target_decel_map = {
        -5: MAX_DECEL,
        0: 0
    }
    
    return linear_interpolation(target_decel_map, value)
