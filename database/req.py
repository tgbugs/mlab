import requests as r
import re

#Test some requests for scraping jax

def getJaxData(stockNOorURL):
    #patterns to match
    sRegex='/(\d+).html'
    nRegex=b'\<title\>JAX\ Mice\ Database'
    cRegex=b'jax:strain:sp:StrainCommonNames'
    aRegex=b'jax:strain.sp:AlleleCommonNames'
    OR=b'|'
    pattern=nRegex+OR+cRegex+OR+aRegex
    title=b'\d\ (.+)\<'
    content=b'content="(.+)"'

    if len(stockNOorURL) > 10:
        url=stockNOorURL
        stockNO=re.search(sRegex,url).group(1)
    else:
        stockNO=stockNOorURL
        url='http://jaxmice.jax.org/strain/%s.html'%stockNO
    #get the raw data
    page=r.get(url)
    page.close()
    lines=page.iter_lines()

    matches=[re.search(pattern,line).string for line in lines if re.search(pattern,line) is not None]
    n=[re.search(nRegex,m).string for m in matches if re.search(nRegex,m) is not None][0]
    c=[re.search(cRegex,m).string for m in matches if re.search(cRegex,m) is not None][0]
    a=[re.search(aRegex,m).string for m in matches if re.search(aRegex,m) is not None][0]

    name=re.search(title,n).group(1).decode('utf-8')
    try: commonNames=re.search(content,c).decode('utf-8')
    except: commonNames=None
    try: alleleNames=re.search(content,a).group(1).decode('utf-8')
    except: alleleNames=None

    return url,stockNO,name,commonNames,alleleNames


ai32='http://jaxmice.jax.org/strain/012569.html'
gin='http://jaxmice.jax.org/strain/003718.html'

adat=getJaxData(ai32)
gdat=getJaxData(gin)

print(adat)
print(gdat)




