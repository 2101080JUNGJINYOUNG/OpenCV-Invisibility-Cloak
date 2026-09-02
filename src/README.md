[![⬅ 루트로 돌아가기](https://img.shields.io/badge/⬅_루트로_돌아가기-2563eb?style=for-the-badge)](../README.md)

# 코드 상세 설명

전체 코드는 [`invisibility_cloak.py`](./invisibility_cloak.py)에 있습니다. 아래는 프로젝트의 핵심 아이디어, 함수 단위 설명, 그리고 메인 루프가 한 프레임을 처리하는 전체 흐름을 코드 기준으로 정리한 것입니다.

프로젝트 전체 소개, 주요 기능 요약, 실행 방법은 [메인 README](../README.md)를 참고하세요.

## 핵심 아이디어

영화 해리포터의 "투명 망토"처럼, 특정 색상의 물체를 비추면 그 부분만 화면에서 사라진 것처럼 보이게 만드는 실시간 영상 처리 프로그램입니다. 원리는 간단합니다: 사람이 없는 배경을 미리 한 장 찍어두고, 이후 매 프레임에서 지정한 색(기본값: 빨강)이 검출된 영역만 그 배경 이미지로 바꿔치기합니다. 색상이 검출된 자리에는 저장해둔 배경이, 나머지 자리에는 지금 촬영 중인 실제 모습이 그대로 나오기 때문에, 색깔 물체를 비춘 부분만 배경과 하나가 되어 "투명해진 것"처럼 보입니다.

## 함수별 설명

- **`get_mask(hsv)`** — 전역 변수 `selected_color`(`'red'` / `'green'` / `'blue'`, 기본값 `'red'`)에 맞는 HSV 범위로 `cv2.inRange()`를 적용해 이진 마스크(해당 색상 영역=255, 나머지=0)를 만듭니다. 빨강은 HSV 색상환에서 0° 부근과 180° 부근 두 군데에 걸쳐 있기 때문에, `[0,120,70]~[10,255,255]`와 `[170,120,70]~[180,255,255]` 두 범위의 마스크를 만들어 더합니다(`+`). 초록은 `[40,50,50]~[85,255,255]`, 파랑은 `[85,110,110]~[130,255,255]` 한 범위로 충분합니다.
- **`fit_text_to_button(text, w, h, font, thickness)`** — `scale = 0.7`에서 시작해 `cv2.getTextSize()`로 잰 글자 크기가 버튼 폭/높이(`w*2, h*2` 이내)를 넘지 않을 때까지 `scale`을 0.01씩 줄여나갑니다(최소 0.1). 버튼 라벨 길이가 달라도("Change BG" vs "B Picture Show") 항상 버튼 안에 딱 맞게 들어가도록 하는 자동 맞춤 함수입니다.
- **`capture_background()`** — 7초 카운트다운(매초 `cap.read()`로 프레임을 갱신하면서 화면에 `"{n}seconds background capture"`를 빨간 글씨로 표시, `cv2.waitKey(1000)`으로 1초씩 대기)을 진행한 뒤, 카운트다운이 끝난 시점의 프레임을 배경으로 저장합니다. `(배경 이미지, 촬영 시각)` 튜플을 반환하며, 프로그램 시작 시 한 번, 그리고 사용자가 "Change BG" 버튼을 누를 때마다 다시 호출됩니다.
- **`draw_button(sidebar, y, label, selected)`** — 사이드바 이미지 위에 사각형 버튼(`cv2.rectangle`)과 중앙 정렬된 라벨(`cv2.putText`)을 그립니다. `selected=True`이면 버튼 색이 회색 `(68,68,68)`에서 빨강 계열 `(100,100,255)`로 바뀌어 방금 클릭됐음을 보여줍니다.
- **`mouse_callback(event, x, y, flags, param)`** — `cv2.setMouseCallback()`으로 등록되는 콜백입니다. 좌클릭 좌표가 사이드바 영역(`10 <= x <= sidebar_width-10`) 안이고 6개 버튼(Change BG / Save Screenshot / B Picture Show / Red / Green / Blue) 중 하나의 y좌표 범위에 들어오면 해당 동작을 실행합니다: Change BG는 `capture_background()`를 재호출, Save Screenshot은 현재 합성 결과(`combined`)를 `screenshot_YYYYmmdd_HHMMSS.png` 형식 파일명으로 `cv2.imwrite()` 저장, B Picture Show는 5초짜리 배경 썸네일 타이머(`picture_show_start_time`)를 시작, Red/Green/Blue는 `selected_color`를 바꿉니다. 어떤 버튼을 눌렀든 `clicked_button`과 `clicked_time`이 갱신되어 0.3초간 버튼이 강조 표시됩니다.

## 메인 루프 처리 순서 (프레임 1장당)

1. **카메라 연결** — `cap = cv2.VideoCapture(0)`으로 내장/외장 카메라를 연결합니다.
2. **배경 캡처 시작** — `capture_background()`를 호출해 7초 딜레이 후 사람이 없는 배경(`background`)과 촬영 시각(`background_capture_time`)을 저장합니다.
3. **메인 루프 시작** — `while cap.isOpened():` 안에서 아래 과정이 매 프레임 반복됩니다.
4. **프레임 읽기 및 전처리** — `ret, frame = cap.read()` 후 `cv2.flip(frame, 1)`로 좌우 반전(거울 모드), `cv2.resize()`로 960×720(`target_width × target_height`) 해상도로 통일합니다.
5. **HSV 색공간 변환** — `hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)`. RGB보다 색상(H) 성분이 조명 변화에 덜 민감해서 색 검출이 쉬워집니다.
6. **색상 마스크 생성** — `mask = get_mask(hsv)`로 선택된 색상 범위만 흰색, 나머지는 검정인 이진 마스크를 만듭니다.
7. **노이즈 제거** — `cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_3x3, iterations=2)`(침식 후 팽창 = 열림 연산, 3×3 커널로 2회 반복)으로 작은 점 잡음을 없애고, `cv2.dilate(mask, kernel_3x3, iterations=1)`로 남은 영역의 경계를 살짝 넓혀 자연스럽게 만듭니다.
8. **작은 객체 제거** — `cv2.findContours()`로 마스크 안의 윤곽선들을 찾고, `cv2.contourArea(cnt) < 2000`인 너무 작은 영역은 `cv2.drawContours(..., -1, 0, -1)`로 마스크에서 지워버립니다(작은 잡음 덩어리가 망토로 오인식되는 것을 방지).
9. **반전 마스크 생성** — `mask_inv = cv2.bitwise_not(mask)`. 망토가 아닌 영역(원본 프레임을 그대로 보여줘야 하는 부분)을 나타냅니다.
10. **망토 영역에 배경 채우기** — `res1 = cv2.bitwise_and(current_bg, current_bg, mask=mask)`로, 저장해둔 배경 이미지에서 마스크(망토) 영역만 잘라냅니다.
11. **비망토 영역에 현재 프레임 유지** — `res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)`로, 현재 프레임에서 망토가 아닌 부분만 잘라냅니다.
12. **두 영상 합성** — `result = cv2.add(res1, res2)`. 두 영역이 서로 겹치지 않는 마스크이므로 단순히 더하기만 해도 자연스럽게 합쳐지고, 이 결과가 "망토가 투명해진" 화면입니다.
13. **사이드바 생성 및 버튼 표시** — 흰색 사이드바(`np.ones((720, 200, 3)) * 255`)를 만들고 `draw_button()`으로 6개 버튼(+"Color Change" 제목)을 그립니다. 최근 0.3초 안에 클릭된 버튼은 `clicked_button`으로 표시되어 색이 강조됩니다.
14. **현재 상태 텍스트 표시** — 사이드바 하단에 `fit_text_to_button()`으로 크기를 맞춘 "Color: Red" 같은 현재 색상, "BG: HH:MM:SS" 같은 배경 촬영 시각을 표시합니다.
15. **화면 합치기** — 사이드바(왼쪽, 200px)와 합성 결과(오른쪽, 960px)를 하나의 `combined`(1160×720) 이미지로 나란히 붙입니다.
16. **배경 썸네일 표시(선택 시)** — "B Picture Show" 버튼을 누르면 `picture_show_start_time`부터 5초 동안, 저장된 배경을 사이드바 폭의 80%·화면 높이의 15% 크기로 축소한 썸네일을 화면 우하단(`combined[-th-10:-10, -tw-10:-10]`, 여백 10px)에 겹쳐 보여줍니다.
17. **마우스 클릭 이벤트 처리** — `mouse_callback()`이 버튼 클릭을 감지해 배경 재촬영, 색상 변경, 스크린샷 저장 등을 즉시 반영합니다.
18. **영상 저장** — `out.write(combined)`으로 UI가 포함된 전체 화면을 `output.mp4`에, `out2.write(combined[:, sidebar_width:])`으로 UI 없이 투명망토 결과만을 `original.mp4`에 각각 기록합니다(둘 다 카메라의 실제 FPS로 저장, FPS를 못 읽으면 30으로 대체).
19. **종료 처리** — `cv2.waitKey(1) & 0xFF == ord('q')`이면 루프를 빠져나와 `cap.release()`, `out.release()`, `out2.release()`, `cv2.destroyAllWindows()`로 모든 리소스를 정리하고 프로그램을 종료합니다.
