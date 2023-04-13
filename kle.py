import numpy as np
import math
import cv2
import serial
ser = serial.Serial("COM8", 9600, timeout = 1000 ) 
c_square,c_triangel , c_Home ,c_Target  = [0,0],[0,0],[0,0],[600, 50]
temp_target = (0,0)
# c_bot = (0,0)
c_obstrcle=[0,0]
ang=0
result =False
p3 = [0, 0]
p4 = [0, 0]
p5 = [0, 0]
p6 = [0, 0]
thick=2    
    
def main(all,obstracle,image):
    # c_square,c_triangel , c_Home ,c_Target  = [0,0],[0,0],[0,0],[600, 50]
    # temp_target = (0,0)
    # # c_bot = (0,0)
    # c_obstrcle=[0,0]
    # ang=0
    img=image
    result0 =False
    result1 =False
    result2 =False
    c_square,c_triangel,c_Home=unpack(all,obstracle)
    print(c_square,c_triangel,'-----------')
    c_Target = [600, 50]
    obstr = obstracle
    c_bot= ( (c_square[0] + c_triangel[0]) / 2 , (c_square[1] + c_triangel[1]) / 2 )
    
    if c_square[0]+c_square[1]==0 and c_triangel[0]+c_triangel[1]==0:
        print("^^^^^^^^^^^^^^^^^^^")
        return img
    
    elif 0<get_distance(c_bot[0], c_bot[1],c_Target[0], c_Target[1])<10:
        s=str(1)
        ser.write(bytes(s, 'utf-8'))
        print("stop")
        return img  
    
    elif c_square[0]+c_square[1]!=0 or c_triangel[0]+c_triangel[1]!=0:
        print("**********")
        c_bot= ((c_square[0] + c_triangel[0]) / 2 , (c_square[1] + c_triangel[1]) / 2 )
        img = cv2.line(img, (int(c_bot[0]),int(c_bot[1])),c_Target, (0, 255, 0), 9) 
        p3,p4,p5,p6=generate_paralel_path_lines(c_bot,c_Target)
        img = cv2.line(img, (int(p3[0]),int(p3[1])),(int(p4[0]),int(p4[1])), (0, 255, 0), thick) 
        img = cv2.line(img, (int(p5[0]),int(p5[1])),(int(p6[0]),int(p6[1])), (0, 255, 0), thick) 
        if len(obstr)!=0:
            
            for i in range(len(obstr)):
                c_obstrcle[0]=(obstr[i][0]+obstr[i][2])/2     
                c_obstrcle[1]=(obstr[i][1]+obstr[i][3])/2   
                result0 = check_obstracle(p1=c_bot,p2=c_Target,area=[[obstracle[i][0],obstracle[i][1],obstracle[i][2],obstracle[i][3]]],ind=0)
                result1 = check_obstracle(p1=p3,p2=p4,area=[[obstracle[i][0],obstracle[i][1],obstracle[i][2],obstracle[i][3]]],ind=0)
                result2 = check_obstracle(p1=p5,p2=p6,area=[[obstracle[i][0],obstracle[i][1],obstracle[i][2],obstracle[i][3]]],ind=0)

                if result0==True or result1==True or result2==True:
                    # img=image.copy()
                    img = cv2.circle(img, (int(c_obstrcle[0]),int(c_obstrcle[1])),50, (0,0,255), thick)
                    temp_target,img = get_tangent(img,c_obstrcle,c_bot,c_Target,(obstr[i][0],obstr[i][1]))
                    if temp_target[0] !=0 and temp_target[1] !=0:
                        img = drive(c1=c_bot,c2=c_triangel,c3=temp_target,img=img )
                        return img
                    else:
                        return img

        if result==False:
            img=drive(c1=c_bot,c2=c_triangel,c3=c_Target,img = img)
        return img
    return img




def generate_paralel_path_lines(p1,p2):
    x1=int(p1[0])
    y1=int(p1[1])
    x2=int(p2[0])
    y2=int(p2[1])

    p3 = [0, 0]
    p4 = [0, 0]
    p5 = [0, 0]
    p6 = [0, 0]
    if x2-x1==0:
        p3[0]=int(x1-25)
        p3[1]=int(y1-25) 
        p4[0]=int(x2-25)
        p4[1]=int(y2-25) 
        p5[0]=int(x1+25)
        p5[1]=int(y1+25)
        p6[0]=int(x2+25)
        p6[1]=int(y2+25)
        return (p3,p4,p5,p6)
    else:
        m=(y2-y1)/(x2-x1)
        c=y1-m*x1
        variable_c=35
        p1x=x1
        p1y=0
        c1=c-variable_c
        p1y=(m*p1x)+c1
        p3[0]=int(p1x)
        p3[1]=int(p1y)
        
        
        p2x=x2
        p2y=0
        c2=c-variable_c
        p2y=m*p2x+c2
        p4[0]=int(p2x)
        p4[1]=int(p2y)
        
        p3x=x1
        p3y=0
        c3=c+variable_c
        p3y=(m*p3x)+c3
        p5[0]=int(p3x)
        p5[1]=int(p3y)

        p4x=x2
        p4y=0
        c4=c+variable_c
        p4y=m*p4x+c4
        p6[0]=int(p4x)
        p6[1]=int(p4y)
        
        return (p3,p4,p5,p6)





def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)            

def unpack(all,obstracle):

    c_square[0]=(all[1][0]+all[1][2])/2     
    c_square[1]=(all[1][1]+all[1][3])/2 

    c_triangel[0]=(all[0][0]+all[0][2])/2     
    c_triangel[1]=(all[0][1]+all[0][3])/2 

    c_Home[0]=(all[2][0]+all[2][2])/2     
    c_Home[1]=(all[2][1]+all[2][3])/2 
    

    # c_Target[0]=(all[3][0]+all[3][2])/2     
    # c_Target[1]=(all[3][1]+all[3][3])/2 
    return c_square,c_triangel,c_Home
def intersection_point(x1, y1, x2, y2, x3, y3, x4, y4):
    A = np.array([[y2-y1, x1-x2], [y4-y3, x3-x4]])
    b = np.array([x1*(y2-y1)-(x2-x1)*y1, x3*(y4-y3)-(x4-x3)*y3])
    try:
        x, y = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return (0,0)  # lines are parallel and do not intersect
    return (x, y)


def check_obstracle(p1,p2,area,ind):
    res=False
    p_1=(int(p1[0]),int(p1[1]))
    p_2=(int(p2[0]),int(p2[1]))
    s1=[[int(area[ind][0]),int(area[ind][1])],[int(area[ind][2]),int(area[ind][1])],[int(area[ind][2]),int(area[ind][3])],[int(area[ind][0]),int(area[ind][3])]]

    for i in range(len(s1)):
        if i == 3:
            x ,y =intersection_point(x1=s1[i][0],y1=s1[i][1],x2=s1[0][0],y2=s1[0][1], x3=int(p1[0]), y3=int(p1[1]), x4=int(p2[0]), y4=int(p2[1]))
        elif i!=3:
            x ,y =intersection_point(x1=s1[i][0],y1=s1[i][1],x2=s1[i+1][0],y2=s1[i+1][1], x3=int(p1[0]), y3=int(p1[1]), x4=int(p2[0]), y4=int(p2[1]))
        
        if (int(area[ind][0])<=x and x<=int(area[ind][2])) and (int(area[ind][1])<=y and y<=int(area[ind][3])) and (p_1[0]<=x and x<=p_2[0]): #and (p_1[1]<=y and y<=p_2[1]) :
            res=True
            break
        else:
            res=False

    return res


def angel_betwn_lines(c1,c2,c3):
    ix=int(c1[0])
    iy=int(c1[1])
    x1=int(c2[0])
    y1=int(c2[1])
    x2=int(c3[0])
    y2=int(c3[1])
    d1=0
    d2=0
    if (x1-ix)==0 and y1>iy:
        d1=90
        print(d1)
        
    elif (x1-ix)==0 and y1<iy: 
        d1=-90
        print(d1)
    elif (x1-ix)!=0:
        d1=np.degrees(math.atan((y1-iy)/(x1-ix)))
        if x1>=ix and y1>=iy:
            d1=d1
        elif x1<=ix and y1>=iy:
            d1=(180+d1)
        elif x1<=ix and y1<=iy:
            d1=-(180-d1) 
        elif x1>=ix and y1<=iy:
            d1=d1     

            
    if  (x2-ix)==0 and y2>iy:
        d2=90
    elif (x2-ix)==0 and y2<iy: 
        d2=-90
        print(d2)
        
    elif (x2-ix)!=0:    
        d2=np.degrees(math.atan((y2-iy)/(x2-ix)))
        if x2>=ix and y2>=iy:
            d2=d2
        elif x2<=ix and y2>=iy:
            d2=(180+d2)
        elif x2<=ix and y2<=iy:
            d2=-(180-d2) 
        elif x2>=ix and y2<=iy:
            d2=d2  
    return d2-d1






def get_tangent(image1,center, point_0 ,target,it):
    # Define the center of the circle
    center = (int(center[0]),int(center[1]))
    # Define the radius of the circle
    radius = int(75+get_distance(center[0],center[1],it[0],it[1]))
    r=get_distance(center[0],center[1],it[0],it[1])
    # Define the point outside of the circle
    external_point = (int(point_0[0]),int(point_0[1]))

    thick=2
    tangent_point1=np.array([0,0])
    tangent_point2=np.array([0,0])
    distance = math.sqrt((external_point[0]-center[0])**2 + (external_point[1]-center[1])**2)
    distance1 = math.sqrt((target[0]-center[0])**2 + (target[1]-center[1])**2)
    if distance <= r or distance1 <= r:
        return((0,0),image1) 
    
    elif distance >= r: 
        # Calculate the angle between the line connecting the external point and the circle's center and the x-axis
        angle = math.atan2(center[1]-external_point[1], center[0]-external_point[0])

        # Calculate the length of the tangent lines
        tangent_length = math.sqrt(distance**2 - r**2)

        # Calculate the angles of the tangent lines
        tangent_angle = math.asin(r/distance)   
        # Calculate the coordinates of the tangent points
        tangent_point1[0] = center[0] + r*math.sin(angle - tangent_angle) 
        tangent_point1[1] = center[1] - r*math.cos(angle - tangent_angle)
        tangent_point2[0] = center[0] - r*math.sin(angle + tangent_angle)
        tangent_point2[1] = center[1] + r*math.cos(angle + tangent_angle)
        los1=get_fake_point((center[0],center[1]),(tangent_point1[0],tangent_point1[1]),radius)
        tangent_point1[0]=los1[0]
        tangent_point1[1]=los1[1]
        los2=get_fake_point((center[0],center[1]),(tangent_point2[0],tangent_point2[1]),radius)
        tangent_point2[0]=los2[0]
        tangent_point2[1]=los2[1]

        g1= get_distance(int(tangent_point1[0]),int(tangent_point1[1]),int(target[0]),int(target[1]))
        g2= get_distance(int(tangent_point2[0]),int(tangent_point2[1]),int(target[0]),int(target[1]))
        if g1>g2:
            tangent_point=(int(tangent_point2[0]),int(tangent_point2[1]))
            image1 = cv2.circle(image1, center,radius, (255,0,0), thick)
            
            image1 = cv2.line(image1, external_point, tangent_point, (0,255,0), thick) 
            g3,g4,g5,g6=generate_paralel_path_lines(external_point,tangent_point)
            image1 = cv2.line(image1, g3, g4, (0,255,0), thick) 
            image1 = cv2.line(image1, g5, g6, (0,255,0), thick) 

            image1= cv2.line(image1,(target[0],target[1]), tangent_point, (0,255,0), thick)
            g7,g8,g9,g10=generate_paralel_path_lines(target,tangent_point)
            image1 = cv2.line(image1, g7, g8, (0,255,0), thick) 
            image1= cv2.line(image1,g9, g10, (0,255,0), thick)


            image1 = cv2.line(image1, external_point, (int(tangent_point1[0]),int(tangent_point1[1])), (0,0,255), thick)
            g11,g12,g13,g14=generate_paralel_path_lines(external_point,tangent_point1)
            image1 = cv2.line(image1, g11, g12, (0,0,255), thick) 
            image1= cv2.line(image1,g13, g14, (0,0,255), thick)

            image1 = cv2.line(image1,(target[0],target[1]), (int(tangent_point1[0]),int(tangent_point1[1])), (0,0,255), thick)
            g15,g16,g17,g18=generate_paralel_path_lines(target,tangent_point1)
            image1 = cv2.line(image1, g15, g16, (0,0,255), thick) 
            image1= cv2.line(image1,g17, g18, (0,0,255), thick)


            
            return (tangent_point,image1)
            
        elif g2>g1:
            tangent_point=(int(tangent_point1[0]),int(tangent_point1[1]))
            image1 = cv2.circle(image1, center,radius, (255,0,0), thick)

            image1 = cv2.line(image1, external_point, tangent_point, (0,255,0), thick)
            g3,g4,g5,g6=generate_paralel_path_lines(external_point,tangent_point)
            image1 = cv2.line(image1, g3, g4, (0,255,0), thick) 
            image1 = cv2.line(image1, g5, g6, (0,255,0), thick) 


            image1 = cv2.line(image1,(target[0],target[1]), tangent_point, (0,255,0), thick)
            g7,g8,g9,g10=generate_paralel_path_lines(target,tangent_point)
            image1 = cv2.line(image1, g7, g8, (0,255,0), thick) 
            image1= cv2.line(image1,g9, g10, (0,255,0), thick)

            image1 = cv2.line(image1, external_point, (int(tangent_point2[0]),int(tangent_point2[1])), (0,0,255), thick) 
            g11,g12,g13,g14=generate_paralel_path_lines(external_point,tangent_point2)
            image1 = cv2.line(image1, g11, g12, (0,0,255), thick) 
            image1= cv2.line(image1,g13, g14, (0,0,255), thick)


            image1 = cv2.line(image1,(target[0],target[1]), (int(tangent_point2[0]),int(tangent_point2[1])), (0,0,255), thick)
            g15,g16,g17,g18=generate_paralel_path_lines(target,tangent_point2)
            image1 = cv2.line(image1, g15, g16, (0,0,255), thick) 
            image1= cv2.line(image1,g17, g18, (0,0,255), thick)

            return (tangent_point,image1)
        elif g1==g2:
            tangent_point=(int(tangent_point2[0]),int(tangent_point2[1]))
            image1 = cv2.circle(image1, center,radius, (255,0,0), thick)

            image1 = cv2.line(image1, external_point, tangent_point, (0,255,0), thick) 
            g3,g4,g5,g6=generate_paralel_path_lines(external_point,tangent_point)
            image1 = cv2.line(image1, g3, g4, (0,255,0), thick) 
            image1 = cv2.line(image1, g5, g6, (0,255,0), thick) 


            image1 = cv2.line(image1,(target[0],target[1]), tangent_point, (0,255,0), thick)
            g7,g8,g9,g10=generate_paralel_path_lines(target,tangent_point)
            image1 = cv2.line(image1, g7, g8, (0,255,0), thick) 
            image1= cv2.line(image1,g9, g10, (0,255,0), thick)


            image1 = cv2.line(image1, external_point, (int(tangent_point2[0]),int(tangent_point2[1])), (0,0,255), thick) 
            g11,g12,g13,g14=generate_paralel_path_lines(external_point,tangent_point2)
            image1 = cv2.line(image1, g11, g12, (0,0,255), thick) 
            image1= cv2.line(image1,g13, g14, (0,0,255), thick)


            image1 = cv2.line(image1,(target[0],target[1]), (int(tangent_point2[0]),int(tangent_point2[1])), (0,0,255), thick)
            g15,g16,g17,g18=generate_paralel_path_lines(target,tangent_point2)
            image1 = cv2.line(image1, g15, g16, (0,0,255), thick) 
            image1= cv2.line(image1,g17, g18, (0,0,255), thick)

            return (tangent_point,image1) 

        
       
    else:
        return((0,0),image1)     




def get_fake_point(a,b,d):
    a = a

    # Ending point of the line
    b = b

    # Distance from starting point to the point on the line
    d = d

    # Find the direction vector of the line
    dir_vector = (b[0] - a[0], b[1] - a[1])

    # Find the magnitude of the direction vector
    dir_mag = math.sqrt(dir_vector[0] ** 2 + dir_vector[1] ** 2)

    # Find the value of t
    t = d / dir_mag

    # Find the point on the line that is a distance of d from the starting point
    r = (round(a[0] + t * dir_vector[0]), round( a[1] + t * dir_vector[1]))
    return r
    




def drive(c1,c2,c3,img):
    ang=angel_betwn_lines(c1,c2,c3)
    print(ang,'angle')
    img= cv2.putText(img, str(ang), (int(c1[0]),int(c1[1])), cv2.FONT_HERSHEY_SIMPLEX,3, (255, 0, 0), 4, cv2.LINE_AA)
    print('text')
    if -10<ang<10:
        print('1tt')
        s=str(0)
        print(s,'ardno')
        ser.write(bytes(s, 'utf-8'))
        print("forward")
        return img  
    elif ang<-5:
        print('2tt')
        s=str(2)
        print(s,'ardno')
        ser.write(bytes(s, 'utf-8'))
        print("left")
        return img  
    elif ang>5:
        print('3tt')
        s=str(3)
        print(s,'ardno')
        ser.write(bytes(s, 'utf-8'))
        print("right")
        return img  
    return img    
    
    
   