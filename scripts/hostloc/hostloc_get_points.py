#-*-coding:utf-8-*-
import requests
import os
import re
import time
import random

# 登录
def login(cookie,number_c):
    url = 'https://www.hostloc.com/member.php?mod=logging&action=login&formhash=eba1bb55'
    res = requests.get(url, cookies=cookie)
    res.encoding = 'utf-8'
    #print(res.text)
    if u'欢迎您回来' in res.text:
        point = re.findall(u"积分: (\d+)", res.text)
        print(u"第", number_c, "个帐户登录成功！当前积分：%s" % point)
        return point
    else:
        print(u"第", number_c, "个帐户登录失败！")
        return 0

# 抓取用户设置页面的积分
def check_point(cookie, number_c):
    url = 'https://www.hostloc.com/member.php?mod=logging&action=login&formhash=eba1bb55'
    res = requests.get(url, cookies=cookie)
    res.encoding = 'utf-8'
    #print(res.text)
    if u'欢迎您回来' in res.text:
        point = re.findall(u"积分: (\d+)", res.text)
        return point
    else:
        print(u"第", number_c, "个帐户查看积分失败，可能已退出")
        return -1


# 随机生成用户空间链接
def randomly_gen_uspace_url():
    url_list = []
    # 访问小黑屋用户空间不会获得积分、生成的随机数可能会重复，这里多生成两个链接用作冗余
    for i in range(12):
        uid = random.randint(10000, 45000)
        url = "https://www.hostloc.com/space-uid-{}.html".format(str(uid))
        url_list.append(url)
    return url_list


# 依次访问随机生成的用户空间链接获取积分
def get_points(cookie, number_c):
    url_list = randomly_gen_uspace_url()
    # 依次访问用户空间链接获取积分，出现错误时不中断程序继续尝试访问下一个链接
    for i in range(len(url_list)):
        url = url_list[i]
        try:
            requests.get(url, cookies=cookie)
            print("第", i + 1, "个用户空间链接访问成功")
            time.sleep(4)  # 每访问一个链接后休眠4秒，以避免触发论坛的防cc机制
        except Exception as e:
            print("链接访问异常：" + str(e))
        continue

if __name__ == "__main__":
    cookie_saltkey = os.environ["HOSTLOC_COOKIE_SALTKEY"]
    cookie_auth = os.environ["HOSTLOC_COOKIE_AUTH"]
    try:
      notify_url = os.environ["NOTIFY_URL"]
    except Exception as e:
      pass

    # 分割用户名和密码为列表
    saltkey_list = cookie_saltkey.split(",")
    auth_list = cookie_auth.split(",")

    if len(saltkey_list) != len(auth_list):
        print("用户名与密码个数不匹配，请检查环境变量设置是否错漏！")
    else:
        print("共检测到", len(saltkey_list), "个帐户，开始获取积分")
        print("*" * 30)

        # 依次登录帐户获取积分，出现错误时不中断程序继续尝试下一个帐户
        success = 0
        for i in range(len(saltkey_list)):
            try:
                # 准备cookie用于登录
                # 可以在Chrome等浏览器手动登录后获取cookie, 根据对应字段修改下面的值即可
                #timestamp = '%d' % (int(time.time()))
                cookie = {
                  'hkCM_2132_saltkey': saltkey_list[i],
                  'hkCM_2132_auth': auth_list[i],
                }
                s = login(cookie, i + 1)
                if s:
                  get_points(cookie, i + 1);
                  p = check_point(cookie, i + 1)
                  if(s == p):
                    print("现在积分：%s，检测到您的积分无变化，可能您已经赚过积分了" % p)
                  else:
                    print("现在积分：%s" % p)
                  print("*" * 30)
                  success = success + 1
            except Exception as e:
                print("获取积分异常：" + str(e))
            continue

        if(len(saltkey_list)-success>0 and notify_url):
          ## 结果推送
          if ' ' not in notify_url[:8]:
            requests.get(notify_url.strip())
          else:
            method = notify_url.split(' ')[0]
            notify_url = notify_url[len(method)+1:].strip()
            if(method.upper() == 'GET'):
              requests.get(notify_url)
            if(method.upper() == 'POST'):
              requests.post(notify_url)
            if(method.upper() == 'PUT'):
              requests.put(notify_url)
        print("程序执行完毕，获取积分过程结束")

