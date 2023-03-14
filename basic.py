"""

"""

import cv2 # opencv 사용
import numpy as np

cap = cv2.VideoCapture('hough_line.mp4') # 동영상 불러오기
i = 0; num = 0
# 영상 열기 성공했을 때 and (현재 프레임 수 = 총 프레임 수)일 때까지 반복
while(cap.isOpened() and cap.get(cv2.CAP_PROP_POS_FRAMES) != cap.get(cv2.CAP_PROP_FRAME_COUNT)):
    
    ret,image = cap.read() # 프레임 받아오기 (ret: 성공여부, image: 현재 프레임)
    if not ret: break # 새로운 프레임을 못받아 왔을 때 break

    #-----< 윤곽선 추출 >-----
    gray_img = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) # 흑백이미지로 변환    
    ga_img=cv2.GaussianBlur(gray_img, (3, 3), 0) # 3*3 가우시안 필터 적용
    canny_img = cv2.Canny(ga_img,100,200) # Canny edge 알고리즘

    #-----< 관심 영역 지정 >-----
    height = image.shape[0]
    width = image.shape[1]
    white_color = (255,255,255)
    point = np.array([[0,height],[0,height/2],[width,height/2],[width,height]], np.int32) # 관심 영역 좌표
    black_img = np.zeros_like(canny_img) # 검은색 배경
    fill_img = cv2.fillPoly(black_img, [point], white_color) # 관심 영역
    edges_img = cv2.bitwise_and(canny_img, fill_img) # 관심 영역 안의 윤곽선 추출

    # if i == 0:
    #     # cv2.imshow('image',image) # 원본
    #     # cv2.waitKey(0)
    #     # cv2.imshow('gray_img',gray_img) # 그레이스케일
    #     # cv2.waitKey(0)
    #     # cv2.imshow('ga_img',ga_img) # 가우시안 필터
    #     # cv2.waitKey(0)
    #     cv2.imshow('canny_img',canny_img) # 윤곽선
    #     cv2.waitKey(0)
    #     cv2.imshow('fill_img',fill_img) # 관심 영역
    #     cv2.waitKey(0)
    #     cv2.imshow('edges_img',edges_img) # 관심 영역에서의 윤곽선
    #     cv2.waitKey(0)

    #----------< 직선 검출 >----------
    min_L = 10 # 선의 최소 길이-->점선
    max_G = 30 # 선사이의 최대 허용간격
    lines=cv2.HoughLinesP(edges_img, 1, np.pi/180, 30, minLineLength=min_L, maxLineGap=max_G) # [(시작점), (끝점)] 반환
    # 추출 이미지, 거리정밀도, 세타정밀도, 스레솔드, 선의 최소길이, 선사이의 최대 허용간격

    Line_array=[]
    for line in lines:
        x1 = int(line[0][0])
        y1 = int(line[0][1])
        x2 = int(line[0][2])
        y2 = int(line[0][3])

        if x2-x1 != 0: slope=(y2-y1)/(x2-x1) # 기울기값

        if abs(slope) > 0.15 and abs(slope) < 0.8: # 특정기울기값을 만족하면
            x0 = int((height+(slope*x1-y1))/slope) # x절편을 구해준다

            if x0 not in Line_array: # 중복 제거
                Line_array.append([x0,x1,y1,x2,y2,slope])
                cv2.line(image, (x1, y1), (x2, y2), (50, 50, 255), 2)#(이미지, 좌표1, 좌표2, 색, 선두께)
            
    #-----< 모여있는 직선끼리 묶음 >-----
    Line_array.sort() # x절편 오름차순
    list_x0 = []; list_s = []
    Larray=[]; Rarray=[]
    index = 0
    for line in Line_array: #이부분의 라인은 라인에 대한 정보를 담고있는 [x절편, x1,y1,x2,y2,slope]를 뜻함
        x0 = line[0]
        slope = line[5]
        check = False
        if index == 0:
            list_x0.append(x0) # x절편 저장
            list_s.append(slope) # 기울기 저장
            check = True # 저장 확인
        else: 
            for j in range(0,len(list_x0)): # 이미 집합에 있는 값과 새로운 값과 비교
                if abs(list_x0[j] - x0) < 30 and abs(list_s[j] - slope) < 0.2: # 모여있는 정도, 기울기 비슷한 정도--★
                    list_x0.append(x0)
                    list_s.append(slope) 
                    check = True # 저장 확인
                    break # 저장했으면 탈출
        
        index+=1;
        if check == False or len(Line_array)==index:
            if list_x0[-1]-list_x0[0] >= 5: # 차선 너비--★
                if sum(list_x0)/len(list_x0) < width/2:
                    Larray.append(list_x0) # 왼쪽 차선
                else:
                    Rarray.append(list_x0) # 오른쪽 차선
            if len(Line_array)!=index:
                list_x0 = [] # 집합 초기화
                list_s = []
                list_x0.append(x0) # 새롭게 집합에 저장
                list_s.append(slope)
   
    #----------< 차선 검출 >----------
    for line in Line_array:
        x0 = line[0]
        x1 = line[1]
        y1 = line[2]
        x2 = line[3]
        y2 = line[4]
        

        if len(Larray) != 0 and len(Rarray) != 0:
            if x0 in Larray[-1]: cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2) # 왼쪽 차선
            if x0 in Rarray[0]: cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2) # 오른쪽 차선

    cv2.imshow("result", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if i == 0:
        print("--왼쪽 차선")
        for a in Larray:
            print(a)
        print("--오른쪽 차선")
        for a in Rarray:
            print(a)
        cv2.waitKey(0)

    #--------< 이동방향 인식 >--------
    if len(Larray) != 0 and len(Rarray) != 0:
        L_x0 = int(sum(Larray[-1])/len(Larray[-1])) # 왼쪽 차선 x절편
        R_x0 = int(sum(Rarray[0])/len(Rarray[0])) # 오른쪽 차선 x절편
        print([L_x0, R_x0], end=" ")

        m_x0 = L_x0+R_x0/2
        move = "차선유지"
        
        if R_x0-L_x0 < width and R_x0-L_x0 > width/2: # 차선 간의 간격--★
            if m_x0 < width/2-300: move = "오른쪽이동"
            elif m_x0 > width/2+300: move = "왼쪽이동"
        else: # 인식오류
            move = "인식오류"
            num += 1
            # cv2.waitKey(0)
        print(move)
    
    i += 1;

print((i-num)/i*100,"%") # 성공적인 인식률

cap.release() # 해제
cv2.destroyAllWindows()
