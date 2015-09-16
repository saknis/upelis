import locale 
import gettext 


DEBUG = True
MAILSENDER="upelis@upe.lt"
MAILRCPTTO="upelis@upe.lt"


CURLOCALE = 'en_US'
#current_locale = 'lt_LT'
LANGUAGES={'ru': 'ru_RU', 'en': 'en_US', 'lt': 'lt_LT', 'ua': 'ua_UA', 'it': 'it_IT', 'lv': 'lv_LV', 'by': 'by_BY', 'pl': 'pl_PL', 'de': 'de_DE'}
LANGUAGESNR={'lt': 1, 'ru': 2, 'en': 3, 'lv': 4, 'pl': 5, 'by': 6, 'ua': 7, 'de': 8, 'it': 9}
LANGUAGESSORT = sorted(LANGUAGESNR.iteritems(), key=lambda (k,v):(v,k))
LOCALEPATH = 'lang/' 
FILEEXT='html'
LANG='lt'
LANGDEF=LANG

TITAUTH = "Vardenis Pavardenis"
#_titauth = "Nerijus Terebas"
VERSION='1.6.3'
DYNABOPT="&amp;font_size=14&amp;button_filename=cloud.png&amp;font_file=Ubuntu-B.ttf&amp;left_width=10&amp;right_width=10"
DYNABFONT="Ubuntu-B.ttf"
CMSNAME="Upelis"
CMSPATH="upelis"
CMSTRANS="upelis"
LANGHTML = "<li><a href=\"/"+CMSPATH+"-%s-%s.%s\"><img src=\"/static/images/flag/%s.gif\" border=\"0\" alt=\"%s\" /></a></li>"
RSSTITLE="Nerijaus Terebo puslapis"
SITE1A='upelis.org'
SITE1B='www.upelis.org'
SITE2A='nerij.us'
SITE2B='www.nerij.us'
SITEDOWN='http://www.upelis.org/static/upelis.zip'
