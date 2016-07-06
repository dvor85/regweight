#!/usr/bin/env python

import smtplib,os,urllib2

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logger
from datetime import *
from os import path
from db import *
from config import *

COMMASPACE = ', '

SELF_PATH=path.dirname(path.realpath(__file__))
log = logger.Logger('regweight', 'sendreg', logger.Logger.NOTICE)

def internet_on():
    try:
        response=urllib2.urlopen('http://mail.ru',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False


def main():
    d=DBreg(SELF_PATH)
    now=datetime.today()
    lastpost_str=d.get_lastpost()
    if lastpost_str is None:
        lastpost_str='1970-01-01'
    #lastpost_str='2014-07-07'

    lastpost_obj=datetime.strptime(lastpost_str,"%Y-%m-%d")
    t_delta=timedelta(hours=0)

    dt=now-lastpost_obj
    if dt.days>0:
        if t_delta==timedelta(0):
            dt_format="%Y-%m-%d"
        else:
            dt_format="%Y-%m-%d %H:%M:%S"

        weights=d.select((lastpost_obj+t_delta).strftime(dt_format),(now+t_delta).strftime(dt_format))
        if len(weights)>0:
            main_msg = MIMEMultipart()
            main_msg['Subject'] = FROM.get('subj')
            main_msg['From'] = FROM.get('mail')
            main_msg['Return-path'] = FROM.get('mail')
            main_msg['To'] = COMMASPACE.join(TO.get('to'))
            main_msg['Cc'] = COMMASPACE.join(TO.get('cc'))
            main_msg['Bcc'] = COMMASPACE.join(TO.get('bcc'))

            text=''
            total=0
            ddate=datetime(1970,1,1)

            for i in range(0, len(weights)+1):
                if i < len(weights):
                    l=weights[i]
                    d_obj=datetime.strptime(str(l[1]),"%Y-%m-%d %H:%M:%S")
                    weight=l[2]

                if ((d_obj-t_delta).date() != ddate.date()) or (i >= len(weights)):
                    if (text != ''):
                        #print ddate.strftime("%Y-%m-%d")
                        #print text
                        msg=MIMEText(text+"\nTOTAL;%d" % total, _subtype='csv')
                        fn=ddate.strftime("%Y-%m-%d")+".csv"
                        msg.add_header('Content-Disposition', 'attachment', filename=fn)
                        main_msg.attach(msg)

                    ddate=d_obj-t_delta
                    text=''
                    total=0

                text+="%s;%s\n" % (d_obj.strftime("%H:%M:%S"), weight)
                total+=weight

            smtp=smtplib.SMTP(FROM.get('smtp', 'localhost'))
            try:
                smtp.ehlo()
                # If we can encrypt this session, do it
                if smtp.has_extn('STARTTLS'):
                    smtp.starttls()
                    smtp.ehlo() # re-identify ourselves over TLS connection

                smtp.login(FROM.get('login'), FROM.get('password'))
                smtp.sendmail(FROM.get('mail'), TO.get('to')+TO.get('cc')+TO.get('bcc'), main_msg.as_string())
                log.d('SENDREG SEND: OK')
                if not d.set_lastpost(now.strftime("%Y-%m-%d")):
                    log.d('SET LASTPOST: FAIL')
            except Exception as e:
                log.e('SENDREG ERROR: '+str(e))
            finally:
                smtp.quit()

if __name__ == '__main__':
    if internet_on():
        #pass
        main()


