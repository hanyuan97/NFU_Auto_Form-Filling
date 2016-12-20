# coding=UTF8
import mechanize
import urllib
import random
from lxml import etree

br = mechanize.Browser()
br.set_handle_robots(False)
br.set_debug_http(True)
br.set_debug_responses(True)
br.set_debug_redirects(True)
br.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")]
acc = ''
indexUrl = 'https://ecare.nfu.edu.tw/'
funUrl = ['desktop', 'desktop/menqs', 'aaiqry/poll', 'aaiqry/studscore']

def getauthimg():
	global br
	img = br.open('https://ecare.nfu.edu.tw/ext/authimg?rnd=0.987123243').read()
	imgfile = file('authimg.jpg', 'wb')
	imgfile.write(img)
	imgfile.close()

def menqs(URL):
	global br, acc, indexUrl
	rp = br.open(URL).read()
	page = etree.HTML(rp)
	try:
		t = page.xpath(u"//input[@id='clss_no']")
		clss_no = t[0].attrib['value']
		postdata = {'data[0][name]' : 'clss_no', 'data[0][value]' : clss_no, 'data[1][name]' : 'acc', 'data[1][value]' : acc}
		t = page.xpath(u"//li[@class='li_qa']")
		del t[-1]
		while True:
			print u'(1)全都非常同意\n(2)全都很同意\n(3)全都有點同意\n(4)全都有點不同意\n(5)全都很不同意\n(6)全都有點不同意\n(7)隨機'.encode('cp950')
			ans = raw_input(u'請選擇：'.encode('cp950'))
			if ans > '7' or ans < '1': 
				print u'輸入錯誤！'.encode('cp950')
			else:
				answer = -1 if ans == '7' else 6 - int(ans)
				break
		for i, ele in enumerate(t):
			n = ele.xpath(u".//input[@value='5']")
			name = n[0].attrib['name']
			postdata['data[' + str(i+2) +'][name]'] = name
			postdata['data[' + str(i+2) +'][value]'] = random.randint(0,5) if answer == -1 else str(answer)

		send = page.xpath(u"//input[@name='send']")[0].attrib['value']
		postdata.update({'data[12][name]' : 'qa11', 'data[12][value]' : '', 'qa11' : '', 'data[13][name]' : 'send', 
						 'data[13][value]' : send})
		data = urllib.urlencode(postdata)
		br2 = br
		br2.addheaders = [('X-Requested-With', 'XMLHttpRequest'),
						  ('Referer', 'https://ecare.nfu.edu.tw/desktop/menqs')]
		if br2.open(indexUrl + 'mentorajax/menqs', data).read() == '1':
			print u'填寫完成！'.encode('cp950')
	except:
		print u'已填寫過或發生錯誤'.encode('cp950')
	br2.close()
	return end()

def poll(URL):
	global br
	rp = br.open(URL).read()
	page = etree.HTML(rp)
	tr = page.xpath(u'//div[@id="div_cge"]/table/tr')
	tr = tr[1:-1]
	tcurl =[]
	print u'請選擇老師\n\n0.一次填完未填的\n'.encode('cp950')
	for i ,a in enumerate(tr):
		print str(i+1) + '.' + ' '.join([ele.text for ele in a[2:4][::-1]])
		print u'未填\n'.encode('cp950') if not a[4].text else u'已完成\n'.encode('cp950')
		tcurl.append(1 if a[4].text else a[4][0][0].attrib['href'][1:])
	print u'e.離開此功能'.encode('cp950')
	while True:
		try:
			ch = raw_input(':')
			if ch == '0':
				poll2(tcurl)
				break
			elif ch == 'e' or ch == 'E':
				return False
			elif tcurl[int(ch)-1] == 1:
				print u'該老師已經填過囉'.encode('cp950')
			elif tcurl[int(ch)-1]:
				poll2([tcurl[int(ch)-1]])
				break
		except:
			print u'別亂填啊我懶著處理例外輸入=_='.encode('cp950')

	return end()

def poll2(tcurl):
	global br, indexUrl
	print u'\n問卷好像有分種類，不保證一定填對，但一定(應該)會幫你填好填滿！！'.encode('cp950')
	print u'老師(只有好棒棒老師會被推薦教師甄選)：'.encode('cp950')
	print u'(1)好棒棒！\n(2)好棒\n(3)還行\n(4)好糟\n(5)好糟糟\n(6)老師誰啊隨便填'.encode('cp950')
	ans_1 = 6 - int(raw_input(':'))
	print u'我是：'
	print u'(1)好棒棒學生\n(2)普通學生\n(3)8+9\n(4)隨便啦'.encode('cp950')
	ans_2 = int(raw_input(':'))
	arrans2 = [[1,1,3,1,2],[2,2,2,2,2],[3,3,1,3,2]]
	
	for tu in tcurl:
		if tu == 1 : continue
		rp = br.open(indexUrl + tu).read()
		br.select_form(nr=0)
		page = etree.HTML(rp)
		table = page.xpath(u"//table[@class='tbcls']")
		del table[0]

		for tr in table[0].xpath(u".//tr")[1:]:
			name = tr[2][0].attrib['name']
			br[name] = [str(random.randint(1, 5))] if ans_1 == 6 else [str(ans_1)]
		for i, tr in enumerate(table[1].xpath(u".//tr")):
			name = tr[2][0].attrib['name']
			br[name] = [str(random.randint(1, 3))] if ans_2 == 4 else [str(arrans2[ans_2][i])]
		br['ansF'] = ['1'] if ans_1 == 5 else ['2']
		br.submit()
	print u'填寫完成！...應該啦！'.encode('cp950')

def studscore(URL):
	global br
	t = br.open(URL).read()
	page = etree.HTML(t)
	a = page.xpath('//tr')
	for ele in a:
		opt = ele.xpath('.//td/text()')
		print '\t'.join(op.strip(' ') for op in opt)
	print br.geturl() + '\n'
	return end()

def end():
	while True:
		print u'\n(1)繼續使用其他功能\n(2)關閉程式\n'.encode('cp950')
		e = raw_input(u'請選擇功能：'.encode('cp950'))
		if e == '1':
			return False
		elif e == '2':
			return True
		else:
			print u'輸入錯誤！(1)\n'.encode('cp950')

def main():
	global br, indexUrl, funUrl, acc
	first = True
	while first or br.geturl() != (indexUrl + funUrl[0]):
		if first: first = False
		else: print u'帳號密碼或驗證碼錯誤！'.encode('cp950')
		getauthimg()
		acc = raw_input(u'帳號：'.encode('cp950'))
		pss = raw_input(u'密碼：'.encode('cp950'))
		authimg = str(raw_input(u'驗證碼：'.encode('cp950'))).upper()
		postdata = { 'login_acc' : acc, 'login_pwd' : pss, 'login_chksum' : authimg }
		data = urllib.urlencode(postdata)
		br.open(indexUrl + 'login/auth', data)
	print u'登入成功！'.encode('cp950')
	#menqs(indexUrl + funUrl[1])
	while True :
		print u'\n(1)導師輔導評量系統\n(2)評量系統\n(3)成績查詢(糞功能)\n(0)結束程式\n'.encode('cp950')
		try:
			f = raw_input(u'請選擇功能：'.encode('cp950'))
			if f == '1' :
				e = menqs(indexUrl + funUrl[1])
			elif f == '2' :
				e = poll(indexUrl + funUrl[2])
			elif f == '3' :
				e = studscore(indexUrl + funUrl[3])
			elif f == '0'  :              
				break
			else :
				print u'別亂輸入ＲＲＲ'.encode('cp950')
			if e:
				break
		except:
			print u'意外錯誤！(1)\n'.encode('cp950')
	br.close()

main()