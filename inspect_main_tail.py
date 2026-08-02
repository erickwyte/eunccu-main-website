from pathlib import Path
text = Path('static/js/main.js').read_text('utf-8')
print('len', len(text))
print('last400')
print(repr(text[-400:]))
print('---')
print(text[-400:])
print('--- counts ---')
for pat in ['});}});','}});})(jQuery)','});});', '})', '}});']:
    print(pat, text.count(pat))
print('sponsor idx', text.find("$('#sponsor-carousel')"))
print('imgpopup idx', text.find("$('.img-popup')"))
print('wow idx', text.find('new WOW().init()'))
print('--- spon region ---')
idx = text.find("$('#sponsor-carousel')")
if idx != -1:
    start = max(0, idx-200)
    end = idx+360
    print(text[start:end])
print('--- imgpopup region ---')
idx2 = text.find("$('.img-popup')")
if idx2 != -1:
    start = max(0, idx2-200)
    end = idx2+260
    print(text[start:end])
print('--- wow region ---')
idx3 = text.find('new WOW().init()')
if idx3 != -1:
    start = max(0, idx3-120)
    end = idx3+260
    print(text[start:end])
