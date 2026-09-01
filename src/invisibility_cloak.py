"""
투명 망토 (Invisibility Cloak) - OpenCV 실시간 영상 처리 프로젝트
6조 컴퓨터 비전 과제

원본 발표/코드 자료(docs/, 이 폴더의 .pdf .hwp)에서 추출한 소스코드를
그대로 실행 가능한 형태로 정리한 파일입니다.

필요 라이브러리: opencv-python, numpy
    pip install opencv-python numpy

실행:
    python invisibility_cloak.py

사용법:
    1. 프로그램을 실행하면 7초 카운트다운 후 현재 화면이 배경으로 저장됩니다.
       이때 카메라 앞에 사람이 없어야 합니다.
    2. 이후 지정한 색상(기본: 빨강)의 천을 몸에 두르면 그 부분이
       배경 이미지로 대체되어 투명해진 것처럼 보입니다.
    3. 왼쪽 사이드바 버튼으로 배경 재촬영(Change BG), 스크린샷 저장(Save Screenshot),
       배경 미리보기(B Picture Show), 색상 변경(Red/Green/Blue)이 가능합니다.
    4. 'q' 키를 누르면 영상 저장 후 종료됩니다.
"""

import cv2
import numpy as np
import datetime
import time

target_width, target_height, sidebar_width = 960, 720, 200

cap = cv2.VideoCapture(0)
cv2.namedWindow("Invisibility Cloak", cv2.WINDOW_NORMAL)

selected_color = 'red'
clicked_button = None
clicked_time = None
picture_show_start_time = None


def get_mask(hsv):
    """선택된 색상 범위에 해당하는 이진 마스크를 생성한다."""
    if selected_color == 'red':
        # 빨강은 HSV 색상환의 양 끝(0 근처와 180 근처)에 걸쳐 있으므로 두 범위를 합친다.
        lower1, upper1 = np.array([0, 120, 70]), np.array([10, 255, 255])
        lower2, upper2 = np.array([170, 120, 70]), np.array([180, 255, 255])
        return cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)
    elif selected_color == 'green':
        return cv2.inRange(hsv, np.array([40, 50, 50]), np.array([85, 255, 255]))
    elif selected_color == 'blue':
        return cv2.inRange(hsv, np.array([85, 110, 110]), np.array([130, 255, 255]))


def fit_text_to_button(text, w, h, font=cv2.FONT_HERSHEY_SIMPLEX, thickness=1):
    """버튼 크기에 맞도록 글자 크기(scale)를 자동으로 줄여준다."""
    scale = 0.7
    while True:
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        if tw <= w * 2 and th <= h * 2:
            break
        scale = max(scale - 0.01, 0.1)
        if scale == 0.1:
            break
    return scale


def capture_background():
    """7초간 카운트다운을 보여주며 대기한 뒤, 사람이 없는 배경 프레임을 저장한다."""
    print("사람이 없는 상태에서 7초간 대기 후 배경 저장")
    for sec in range(7, 0, -1):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (target_width, target_height))
        cv2.putText(frame, f"{sec}seconds background capture", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.imshow("Invisibility Cloak", frame)
        cv2.waitKey(1000)
    ret, bg = cap.read()
    if not ret:
        print("Background capture failed!")
        exit()
    bg = cv2.flip(bg, 1)
    bg = cv2.resize(bg, (target_width, target_height))
    return bg, datetime.datetime.now()


btn_h = int(target_height * 0.1)
btn_m = int(target_height * 0.01)
font_thick = max(1, btn_h // 35)

y_change_bg = 10
y_save_shot = y_change_bg + btn_h + btn_m
y_b_picture_show = y_save_shot + btn_h + btn_m
y_color_title = y_b_picture_show + btn_h + btn_m
y_red = y_color_title + btn_h + btn_m
y_green = y_red + btn_h + btn_m
y_blue = y_green + btn_h + btn_m


def draw_button(sidebar, y, label, selected=False):
    c = (100, 100, 255) if selected else (68, 68, 68)
    font_scale = fit_text_to_button(label, sidebar_width - 20, btn_h, thickness=font_thick)
    cv2.rectangle(sidebar, (10, y), (sidebar_width - 10, y + btn_h), c, -1)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thick)
    x = (sidebar_width - tw) // 2
    y_text = y + (btn_h + th) // 2 - 3
    cv2.putText(sidebar, label, (x, y_text), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (255, 255, 255), font_thick)


def mouse_callback(event, x, y, flags, param):
    global background, background_capture_time, selected_color
    global clicked_button, clicked_time, picture_show_start_time

    if event == cv2.EVENT_LBUTTONDOWN and 10 <= x <= sidebar_width - 10:
        if y_change_bg <= y <= y_change_bg + btn_h:
            background, background_capture_time = capture_background()
            clicked_button = "Change BG"
        elif y_save_shot <= y <= y_save_shot + btn_h:
            filename = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
            cv2.imwrite(filename, combined)
            print(f"Saved screenshot to {filename}")
            clicked_button = "Save"
        elif y_b_picture_show <= y <= y_b_picture_show + btn_h:
            clicked_button = "B Picture Show"
            picture_show_start_time = time.time()
        elif y_red <= y <= y_red + btn_h:
            selected_color = 'red'
            clicked_button = "Red"
        elif y_green <= y <= y_green + btn_h:
            selected_color = 'green'
            clicked_button = "Green"
        elif y_blue <= y <= y_blue + btn_h:
            selected_color = 'blue'
            clicked_button = "Blue"
        clicked_time = time.time()


cv2.setMouseCallback("Invisibility Cloak", mouse_callback)

fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 30

out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps,
                       (target_width + sidebar_width, target_height))
out2 = cv2.VideoWriter('original.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps,
                        (target_width, target_height))

background, background_capture_time = capture_background()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (target_width, target_height))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = get_mask(hsv)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < 2000:
            cv2.drawContours(mask, [cnt], -1, 0, -1)

    mask_inv = cv2.bitwise_not(mask)
    current_bg = background.copy()
    res1 = cv2.bitwise_and(current_bg, current_bg, mask=mask)
    res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.add(res1, res2)

    sidebar = np.ones((target_height, sidebar_width, 3), dtype=np.uint8) * 255
    if clicked_time and time.time() - clicked_time > 0.3:
        clicked_button = None

    draw_button(sidebar, y_change_bg, "Change BG", clicked_button == "Change BG")
    draw_button(sidebar, y_save_shot, "Save Screenshot", clicked_button == "Save")
    draw_button(sidebar, y_b_picture_show, "B Picture Show", clicked_button == "B Picture Show")

    font_scale = fit_text_to_button("Color Change", sidebar_width - 20, btn_h, thickness=font_thick)
    (tw, th), _ = cv2.getTextSize("Color Change", cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thick)
    x = (sidebar_width - tw) // 2
    y_text = y_color_title + (btn_h + th) // 2 - 3
    cv2.putText(sidebar, "Color Change", (x, y_text), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (0, 0, 0), font_thick)

    draw_button(sidebar, y_red, "Red", clicked_button == "Red")
    draw_button(sidebar, y_green, "Green", clicked_button == "Green")
    draw_button(sidebar, y_blue, "Blue", clicked_button == "Blue")

    color_text = f"Color: {selected_color.capitalize()}"
    font_scale_color = fit_text_to_button(color_text, sidebar_width - 20, btn_h, thickness=font_thick)
    (cw, ch), _ = cv2.getTextSize(color_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale_color, font_thick)
    cv2.putText(sidebar, color_text, ((sidebar_width - cw) // 2, target_height - 80),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale_color, (0, 0, 0), font_thick)

    bg_text = f"BG: {background_capture_time.strftime('%H:%M:%S')}"
    font_scale_bg = fit_text_to_button(bg_text, sidebar_width - 20, btn_h, thickness=font_thick)
    (bw, bh), _ = cv2.getTextSize(bg_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale_bg, font_thick)
    cv2.putText(sidebar, bg_text, ((sidebar_width - bw) // 2, target_height - 50),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale_bg, (0, 0, 0), font_thick)

    combined = np.zeros((target_height, target_width + sidebar_width, 3), dtype=np.uint8)
    combined[:, :sidebar_width] = sidebar
    combined[:, sidebar_width:] = result

    if picture_show_start_time and time.time() - picture_show_start_time <= 5:
        tw, th = int(sidebar_width * 0.8), int(target_height * 0.15)
        thumb = cv2.resize(background, (tw, th))
        combined[-th - 10:-10, -tw - 10:-10] = thumb
    else:
        picture_show_start_time = None

    cv2.imshow("Invisibility Cloak", combined)
    out.write(combined)
    out2.write(combined[:, sidebar_width:])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
out2.release()
cv2.destroyAllWindows()
