import tkinter
import threading
import time
import pyautogui
import sys
from PIL import Image, ImageFilter
import datetime

# 窗口
root = tkinter.Tk()
root.wm_attributes('-topmost', 1)
root.title('斗地主记牌器')
# root.geometry('280x150')
root.geometry('660x250')
root.resizable(0, 0)
lamp = tkinter.Button(root, text=' ', width=3, height=1)
lamp.place(x=550, y=10)  # 状态指示灯

# 界面变量
alphaInEntry = tkinter.StringVar()
num_dw = tkinter.StringVar()  # 大王
num_xw = tkinter.StringVar()  # 小王
num_2 = tkinter.StringVar()  # 2
num_A = tkinter.StringVar()  # A
num_K = tkinter.StringVar()  # K
num_Q = tkinter.StringVar()  # Q
num_J = tkinter.StringVar()  # J
num_10 = tkinter.StringVar()  # 10
num_9 = tkinter.StringVar()  # 9
num_8 = tkinter.StringVar()  # 8
num_7 = tkinter.StringVar()  # 7
num_6 = tkinter.StringVar()  # 6
num_5 = tkinter.StringVar()  # 5
num_4 = tkinter.StringVar()  # 4
num_3 = tkinter.StringVar()  # 3
num_left = tkinter.StringVar()  # 上家
num_me = tkinter.StringVar()  # 自己
num_right = tkinter.StringVar()  # 下家
radio = tkinter.IntVar()  # 选择截图还是屏幕
PicName = tkinter.StringVar()  # 截图文件名

# 数据
cards = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1]
# 牌     空  A  2  3  4  5  6  7  8  9  10 J  Q  K  小 大
myConfidence = 1  # 我的牌的置信度
otherConfidence = 1  # 别人的牌的置信度
whiteConfidence = 1  # 检测白块的置信度
waitTime = 1  # 等待状态稳定延时
myFilter = 40  # 我的牌检测结果过滤参数
otherFilter = 25  # 别人的牌检测结果过滤参数
sleepTime = 0.05  # 循环中睡眠时间

# 坐标
myPos = (0, 0, 0, 0)  # 我的截图区域
lPos = (0, 0, 0, 0)  # 左边截图区域
rPos = (0, 0, 0, 0)  # 右边截图区域
cPos = (0, 0, 0, 0)  # 底牌截图区域
mpPos = (0, 0, 0, 0)  # 明牌截图区域

# 信号量
shouldExit = 0  # 通知上一轮记牌结束
canRecord = threading.Lock()  # 开始记牌

CardsNum = {'rdw': 1,
            'bxw': 1,
            'b2': 2,
            'r2': 2,
            'bA': 2,
            'rA': 2,
            'bK': 2,
            'rK': 2,
            'bQ': 2,
            'rQ': 2,
            'bJ': 2,
            'rJ': 2,
            'b10': 2,
            'r10': 2,
            'b9': 2,
            'r9': 2,
            'b8': 2,
            'r8': 2,
            'b7': 2,
            'r7': 2,
            'b6': 2,
            'r6': 2,
            'b5': 2,
            'r5': 2,
            'b4': 2,
            'r4': 2,
            'b3': 2,
            'r3': 2,
            }


def setAlpha():
    global alphaInEntry
    root.attributes('-alpha', float(alphaInEntry.get()))


def on_closing():
    global shouldExit
    if shouldExit == 0:
        stop()
    else:
        root.destroy()


def initial():
    global myPos, lPos, rPos, cPos, mpPos, myConfidence, otherConfidence, whiteConfidence, waitTime, myFilter, otherFilter, sleepTime, Started, haveThread
    f = open('settings.txt', 'r', encoding='utf-8')
    alphaInEntry.set(f.readline().split(' ')[0])  # 读取透明度
    my = f.readline().split(' ')
    myPos = (int(my[0]), int(my[1]), int(my[2]), int(my[3]))
    left = f.readline().split(' ')
    lPos = (int(left[0]), int(left[1]), int(left[2]), int(left[3]))
    right = f.readline().split(' ')
    rPos = (int(right[0]), int(right[1]), int(right[2]), int(right[3]))
    center = f.readline().split(' ')
    cPos = (int(center[0]), int(center[1]), int(center[2]), int(center[3]))
    center = f.readline().split(' ')
    mpPos = (int(center[0]), int(center[1]), int(center[2]), int(center[3]))
    myConfidence = float(f.readline().split(' ')[0])
    otherConfidence = float(f.readline().split(' ')[0])
    whiteConfidence = float(f.readline().split(' ')[0])
    waitTime = float(f.readline().split(' ')[0])
    myFilter = int(f.readline().split(' ')[0])
    otherFilter = int(f.readline().split(' ')[0])
    sleepTime = float(f.readline().split(' ')[0])
    Started = False     #是否开始新局，默认未开始
    haveThread = False  #是否已启动线程
    f.close()


def loadCardsNum():  # 显示牌的数目
    global cards, num_dw, num_xw, num_2, num_A, num_K, num_Q, num_J, num_10, num_9, num_8, num_7, num_6, num_5
    global num_4, num_3
    global lamp

    strCards = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    # 牌         空  A   2   3   4   5   6   7   8   9   10  J   Q   K   小   大
    for i in range(16):
        if cards[i] == 0:
            strCards[i] = ''
        else:
            strCards[i] = str(cards[i])

    num_dw.set(strCards[15])
    num_xw.set(strCards[14])
    num_2.set(strCards[2])
    num_A.set(strCards[1])
    num_K.set(strCards[13])
    num_Q.set(strCards[12])
    num_J.set(strCards[11])
    num_10.set(strCards[10])
    num_9.set(strCards[9])
    num_8.set(strCards[8])
    num_7.set(strCards[7])
    num_6.set(strCards[6])
    num_5.set(strCards[5])
    num_4.set(strCards[4])
    num_3.set(strCards[3])

    # lamp.config(background='springgreen')


def cardsFilter(location, distance):  # 牌检测结果滤波
    if len(location) == 0:
        return 0
    locList = [location[0][0]]
    count = 1
    for e in location:
        flag = 1  # “是新的”标志
        for have in locList:
            if abs(e[0] - have) <= distance:
                flag = 0
                break
        if flag:
            count += 1
            locList.append(e[0])
    return count


def findMyCards():
    global cards, lamp, CardsNum
    myCardsNum = {'rdw': 0,
                  'bxw': 0,
                  'b2': 0,
                  'r2': 0,
                  'bA': 0,
                  'rA': 0,
                  'bK': 0,
                  'rK': 0,
                  'bQ': 0,
                  'rQ': 0,
                  'bJ': 0,
                  'rJ': 0,
                  'b10': 0,
                  'r10': 0,
                  'b9': 0,
                  'r9': 0,
                  'b8': 0,
                  'r8': 0,
                  'b7': 0,
                  'r7': 0,
                  'b6': 0,
                  'r6': 0,
                  'b5': 0,
                  'r5': 0,
                  'b4': 0,
                  'r4': 0,
                  'b3': 0,
                  'r3': 0,
                  }
    CardsNum = {'rdw': 1,
                'bxw': 1,
                'b2': 2,
                'r2': 2,
                'bA': 2,
                'rA': 2,
                'bK': 2,
                'rK': 2,
                'bQ': 2,
                'rQ': 2,
                'bJ': 2,
                'rJ': 2,
                'b10': 2,
                'r10': 2,
                'b9': 2,
                'r9': 2,
                'b8': 2,
                'r8': 2,
                'b7': 2,
                'r7': 2,
                'b6': 2,
                'r6': 2,
                'b5': 2,
                'r5': 2,
                'b4': 2,
                'r4': 2,
                'b3': 2,
                'r3': 2,
                }

    lamp.config(background='red')

    cards = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1]  # 初始化
    # 牌     空  A  2  3  4  5  6  7  8  9  10 J  Q  K  小 大
    loadCardsNum()
    num_left.set("")
    num_right.set("")

    CardCount = 0
    hW = haveWhite(cPos)
    if hW == 1:
        time.sleep(sleepTime * 2)
        img = pyautogui.screenshot(region=myPos)
        for i in myCardsNum.keys():
            result = pyautogui.locateAll(needleImage='pics\\m' + i + '.png', haystackImage=img, confidence=myConfidence)
            myCardsNum[i] = cardsFilter(list(result), myFilter)
            CardCount = CardCount + myCardsNum[i]
            CardsNum[i] -= myCardsNum[i]

        cards[1] -= myCardsNum['bA'] + myCardsNum['rA']
        cards[2] -= myCardsNum['b2'] + myCardsNum['r2']
        cards[3] -= myCardsNum['b3'] + myCardsNum['r3']
        cards[4] -= myCardsNum['b4'] + myCardsNum['r4']
        cards[5] -= myCardsNum['b5'] + myCardsNum['r5']
        cards[6] -= myCardsNum['b6'] + myCardsNum['r6']
        cards[7] -= myCardsNum['b7'] + myCardsNum['r7']
        cards[8] -= myCardsNum['b8'] + myCardsNum['r8']
        cards[9] -= myCardsNum['b9'] + myCardsNum['r9']
        cards[10] -= myCardsNum['b10'] + myCardsNum['r10']
        cards[11] -= myCardsNum['bJ'] + myCardsNum['rJ']
        cards[12] -= myCardsNum['bQ'] + myCardsNum['rQ']
        cards[13] -= myCardsNum['bK'] + myCardsNum['rK']
        cards[14] -= myCardsNum['bxw']
        cards[15] -= myCardsNum['rdw']

    if (CardCount == 17 or CardCount == 20) and hW == 1:  # 17或20张牌，且叫牌完成,新局开始
        return True
    else:
        return False


def findOtherCards(pos):  # 检测pos内的牌
    global cards, lamp, CardsNum
    otherCardsNum = {'rdw': 0,
                     'bxw': 0,
                     'b2': 0,
                     'r2': 0,
                     'bA': 0,
                     'rA': 0,
                     'bK': 0,
                     'rK': 0,
                     'bQ': 0,
                     'rQ': 0,
                     'bJ': 0,
                     'rJ': 0,
                     'b10': 0,
                     'r10': 0,
                     'b9': 0,
                     'r9': 0,
                     'b8': 0,
                     'r8': 0,
                     'b7': 0,
                     'r7': 0,
                     'b6': 0,
                     'r6': 0,
                     'b5': 0,
                     'r5': 0,
                     'b4': 0,
                     'r4': 0,
                     'b3': 0,
                     'r3': 0,
                     }
    # lamp.config(background='red')
    # time.sleep(waitTime)
    img = pyautogui.screenshot(region=pos)

    strCard = ""
    for i in otherCardsNum.keys():
        # 跳过张数为0的检测，提高识别速度
        if i == 'rdw':
            n = 15
        elif i == 'bxw':
            n = 14
        elif i[1] == 'A':
            n = 1
        elif i[1] == 'K':
            n = 13
        elif i[1] == 'Q':
            n = 12
        elif i[1] == 'J':
            n = 11
        else:
            n = int(i[1:])
        if cards[n] <= 0:
            continue
        # print(i,CardsNum[i])
        if CardsNum[i] <= 0:
            continue

        result = pyautogui.locateAll(needleImage='pics\\o' + i + '.png', haystackImage=img, confidence=otherConfidence)
        otherCardsNum[i] = cardsFilter(list(result), otherFilter)
        num = otherCardsNum[i]
        cards[n] -= num
        CardsNum[i] -= num
        while num > 0:
            num = num - 1
            if i == 'rdw':
                strCard = strCard + "大"
            elif i == 'bxw':
                strCard = strCard + "小"
            else:
                strCard = strCard + i[1:]
    strCard = strCard + " "

    return strCard


def haveWhite(pos):  # 是否有白块
    # 减少检测区域，提高处理速度
    if pos == rPos:
        pos1 = (pos[0] + pos[2] - 100, pos[1], 150, 250)  # 右边出牌靠右
    elif pos == lPos:
        pos1 = (pos[0], pos[1], 200, 250)
    else:
        pos1 = pos
    result = pyautogui.locateOnScreen('pics\\white.png', region=pos1, confidence=whiteConfidence)
    if result is None:
        return 0
    else:
        return 1


def stop():
    global shouldExit, lamp, haveThread
    shouldExit = 1
    lamp.config(background='yellow')

#开启2个线程，分别记上家和下家出牌，提高速度
def start():
    global t, t1, haveThread
    if haveThread == False:
        haveThread = True
        t = threading.Thread(target=startRecord)
        t.setDaemon(True)
        t.start()
        t1 = threading.Thread(target=startRecord_right)
        t1.setDaemon(True)
        t1.start()


#记上家的出牌
def startRecord():  # 开始记牌_上家
    global shouldExit, canRecord, Started, haveThread
    global cards

    print('开始记牌\n', end='')
    shouldExit = 1
    cards = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1]  # 重置牌的数目

    shouldExit = 0
    while not shouldExit:
        # 判断新一轮发牌是否完成，以开始记牌
        while not findMyCards():
            if not shouldExit:
                time.sleep(sleepTime)
            else:
                return

        loadCardsNum()
        num_right.set("")
        num_left.set("")
        Started = True  #新的一局开始了
        lmod = 0  # 左边人上一次的状态，0代表没有出牌，1代表已经出牌
        while not shouldExit:  # 是否有底牌按钮，判断是否新一轮开始，如果新一轮开始，退出此循环
            # 间隔1秒以上没有底牌显示，则本轮结束，防止王炸特效误判
            if haveWhite(cPos) == 0:
                time.sleep(sleepTime * 10)
                if haveWhite(cPos) == 0:
                    Started = False #本局结束
                    break
            lW = haveWhite(lPos)
            if lmod == 0 and lW == 1 and (not shouldExit):  # 左边的人刚才没出牌，现在出牌了
                time.sleep(sleepTime * 5)  # 延迟处理，防止特效影响判断
                #canRecord.acquire() #加锁
                num_left.set(num_left.get() + findOtherCards(lPos))
                loadCardsNum()
                #canRecord.release() #释放锁
                lmod = 1
            if lmod == 1 and lW == 0 and (not shouldExit):  # 左边的人刚刚出牌了，现在牌没了
                lmod = 0
            time.sleep(sleepTime / 2)
    haveThread = False
    #canRecord.release()

#记下家的出牌
def startRecord_right():  # 开始记牌_下家
    global shouldExit, canRecord, Started
    global cards

    while not shouldExit:
        # 判断新一轮发牌是否完成，以开始记牌
        while not Started:
            if not shouldExit:
                time.sleep(sleepTime)
            else:
                return
        rmod = 0  # 同理
        num_right.set("")
        while not shouldExit:
            if not Started:
                break
            rW = haveWhite(rPos)
            if rmod == 0 and rW == 1 and (not shouldExit):  # 右边的人刚才没出牌，现在出牌了
                time.sleep(sleepTime * 6)  # 延迟处理，防止特效影响判断  8月8日由8改为6
                #canRecord.acquire() #加锁
                num_right.set(num_right.get() + findOtherCards(rPos))
                loadCardsNum()
                #canRecord.release() #解除锁
                rmod = 1
            if rmod == 1 and rW == 0 and (not shouldExit):  # 右边人刚刚出牌了，现在牌没了
                rmod = 0
            time.sleep(sleepTime / 2)

# 截图以生成牌点模版 ( 测试 或 制作牌点模板用 ）
def GetCard():
    if radio.get() == 1:
        # 以截屏方式牌点模版
        #FileName = "./ScreenPic/M" + datetime.datetime.now().strftime('%H%M%S')
        #img = pyautogui.screenshot()
        img = Image.open("./ScreenPic/M175052.png")
        Get_Config_IMG(img)
        return
        img.save(FileName + ".png")

    elif radio.get() == 2:
        # 以读文件方式生成牌点模版
        FileName = "./ScreenPic/" + PicName.get()
        if len(FileName) == 0:
            print("请输入截图文件名")
            return
        img = Image.open(FileName + ".png")

        print(img.size[0], img.size[1])

        """ 测试白块 或裁剪图片保存"""
        lPosXy = [lPos[0], lPos[1], lPos[0] + 200, lPos[1] + 250]
        rPosXy = [rPos[0] + rPos[2] - 100, rPos[1], rPos[0] + rPos[2] + 50, rPos[1] + 250]

        # cPosXy = [cPos[0],cPos[1],cPos[0]+cPos[2],cPos[1]+cPos[3]]
        #mpXy = [1310, 1250, 1390, 1300]  # 明牌位置
        print(lPosXy, rPosXy, haveWhite(lPos), haveWhite(rPos))
        img.crop(lPosXy).save(FileName + "_l" + '.png')
        img.crop(rPosXy).save(FileName + "_r" + '.png')
        # img=Image.open(FileName+"_m_"+'.png')
        # print(pyautogui.locate(needleImage='pics\\white.png', haystackImage=img, confidence=myConfidence))
        return
    else:
        return

    im = img
    split_lines = []
    # 自己第一张牌截图位置横坐标
    split_lines.append(645)
    # 经过调整过的分割线的合理间距
    for i in range(17):
        split_lines.append(split_lines[2 * i] + 65)
        split_lines.append(split_lines[2 * i + 1] + 11)
    y_min = 1410  # 自己牌的纵坐标
    y_max = 1490  # 自己牌的高
    c = 1
    for x_min, x_max in zip(split_lines[:-1], split_lines[1:]):
        if x_max - x_min > 20:
            im.crop([x_min, y_min, x_max, y_max]).save(FileName + "_m_" + str(c) + '.png')  # crop()函数是截取指定图像！save保存图像！
        c = c + 1

    """别人的牌截图"""
    y_min = 910  # 别人牌的纵坐标
    y_max = 960
    # 左手边牌
    l_split_lines = []
    l_split_lines.append(677)  # 左边人出牌横坐标
    # 经过调整过的分割线的合理间距
    for i in range(10):
        l_split_lines.append(l_split_lines[2 * i] + 35)
        l_split_lines.append(l_split_lines[2 * i + 1] + 11)
    c = 1
    for x_min, x_max in zip(l_split_lines[:-1], l_split_lines[1:]):
        if x_max - x_min > 20:
            im.crop([x_min, y_min, x_max, y_max]).save(FileName + "_l_" + str(c) + '.png')  # crop()函数是截取指定图像！save保存图像！
        c = c + 1

    # 右手边牌
    r_split_lines = []
    r_split_lines.append(1460)  # 右边人出牌横坐标
    # 经过调整过的分割线的合理间距
    for i in range(10):
        r_split_lines.append(r_split_lines[2 * i] + 35)
        r_split_lines.append(r_split_lines[2 * i + 1] + 11)
    c = 1
    for x_min, x_max in zip(r_split_lines[:-1], r_split_lines[1:]):
        if x_max - x_min > 20:
            im.crop([x_min, y_min, x_max, y_max]).save(FileName + "_r_" + str(c) + '.png')  # crop()函数是截取指定图像！save保存图像！
        c = c + 1

    """
    #两层出牌情况
    #右手边上层牌    
    y_min=830  #别人牌的上层纵坐标
    y_max=880
    r_split_lines=[]    #清空数组
    r_split_lines.append(1460) #右边人出牌横坐标
    # 经过调整过的分割线的合理间距
    for i in range(10):
        r_split_lines.append(r_split_lines[2*i]+35)
        r_split_lines.append(r_split_lines[2*i+1]+11)
    c=1
    for x_min,x_max in zip(r_split_lines[:-1],r_split_lines[1:]):
       im.crop([x_min,y_min,x_max,y_max] ).save(FileName+"_dru_"+str(c)+'.png')       # crop()函数是截取指定图像！save保存图像！
       c=c+1
    #右手边下层牌    
    y_min=910  #别人牌的上层纵坐标
    y_max=960
    r_split_lines=[]    #清空数组
    r_split_lines.append(1460) #右边人出牌横坐标
    # 经过调整过的分割线的合理间距
    for i in range(10):
        r_split_lines.append(r_split_lines[2*i]+35)
        r_split_lines.append(r_split_lines[2*i+1]+11)
    c=1
    for x_min,x_max in zip(r_split_lines[:-1],r_split_lines[1:]):
       im.crop([x_min,y_min,x_max,y_max] ).save(FileName+"_drd_"+str(c)+'.png')       # crop()函数是截取指定图像！save保存图像！
       c=c+1
    """
    return

def Get_Config_IMG(im):
    Result = []
    FindPix = False
    sizeX, sizeY = pyautogui.size()
    #Result = pyautogui.locateAll(needleImage='pics\\split_x.png', haystackImage=im, confidence=0.98)
    Result = pyautogui.locateAll(needleImage='pics\\split_x.png', haystackImage=im, confidence=0.92)
    listResult = list(Result)
    print("begin")
    if len(listResult) == 0:
        return 0
    Old = (0,0,0,0)
    for x in listResult:
        #print(x)
        if abs(x[0] - Old[0]) > 1:
            print(Old,x)
        Old = x
    #im.crop((1200,0,1300,200)).save("11.png")
    #im.crop((700, 800, 1200, 1000)).save("12.png")
    #im.crop((700, 1400, 1700, 1600)).save("13.png")
    im.crop((1970, 1394, 2020, 1396)).save("14.png")
    #im.crop((1970, 1394, 2070, 1700)).save("14.png")




if __name__ == '__main__':
    initial()  # 初始化

    # 设置透明度
    tkinter.Entry(root, textvariable=alphaInEntry, width=4).place(x=310, y=155)
    tkinter.Button(root, text='设置透明度', command=setAlpha).place(x=380, y=145)
    setAlpha()

    # 设置检测区域
    # tkinter.Button(root, text='设置检测区域', command=setScanArea).place(x=20, y=115)

    # 开始记牌
    tkinter.Button(root, text='开始', command=start).place(x=200, y=145)

    # 停止记牌，调试用
    # tkinter.Button(root, text='stop', font=('', 11), command=stop).place(x=5, y=135)
    tkinter.Button(root, text='stop', command=stop).place(x=10, y=145)

    # 截屏生成牌点模版，调试用
    # tkinter.Button(root, text='stop', font=('', 11), command=stop).place(x=5, y=135)
    tkinter.Button(root, text='截屏', command=GetCard).place(x=100, y=145)

    # tkinter.Checkbutton(root,cnf={'屏幕','图片'}).place(100,150)
    radio = tkinter.IntVar()
    tkinter.Radiobutton(root, text="屏幕", variable=radio, value=1, command="").place(x=10, y=205)
    tkinter.Radiobutton(root, text="截图", variable=radio, value=2, command="").place(x=90, y=205)
    tkinter.Label(root, text="请输入文件名", width=12).place(x=180, y=205)
    tkinter.Entry(root, textvariable=PicName, width=10).place(x=350, y=205)
    radio.set(1)

    # 显示
    x_start = 20
    y_start = 5
    x_add = 30
    x_dif = 4
    y_dif = 30
    tkinter.Label(root, text='大', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_dw, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='小', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_xw, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='2', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_2, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='A', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_A, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='K', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_K, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='Q', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_Q, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='J', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_J, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    # x_start = 20
    # y_start = 70
    x_start += x_add
    tkinter.Label(root, text='10', font=('', 10), width=2).place(x=x_start - 2, y=y_start)
    tkinter.Entry(root, textvariable=num_10, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='9', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_9, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='8', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_8, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='7', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_7, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='6', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_6, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='5', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_5, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='4', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_4, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='3', font=('', 10), width=2).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_3, font=('', 10), width=2).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start = 5
    y_start += 2 * y_dif + 5
    tkinter.Label(root, text='上家：', font=('', 10), width=6).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_left, font=('', 10), width=40).place(x=x_start + 80, y=y_start + 1)

    # y_start += y_dif+5
    # tkinter.Label(root, text='自己：', font=('', 10), width=6).place(x=x_start, y=y_start)    #自己没必要显示
    # tkinter.Entry(root, textvariable=num_me, font=('', 10), width=40).place(x=x_start + 80, y=y_start+1 )

    y_start += y_dif + 5
    tkinter.Label(root, text='下家：', font=('', 10), width=6).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_right, font=('', 10), width=40).place(x=x_start + 80, y=y_start + 1)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
