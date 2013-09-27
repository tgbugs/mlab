#tests some reqeusts

import requests as r
import re

ai32='http://jaxmice.jax.org/strain/012569.html'
gin='http://jaxmice.jax.org/strain/003718.html'

def getStrainJaxData(stockNOorURL):
    if len(stockNOorURL) > 10:
        url=stockNOorURL
        stockNO=
    else:
        stockNO=stockNOorURL
        url='http://jaxmice.jax.org/strain/%s.html'%stockNO

    page=r.get(url)
    lines=page.iter_lines()
    page.close()
    name=b"\<title\>JAX\ Mice\ Database"
    common=b"jax:strain:sp:StrainCommonNames"
    allele=b"jax:strain.sp:AlleleCommonNames"
    OR=b"|"
    pattern=name+OR+common+OR+allele
    matches=[re.search(pattern,line).string for line in lines if re.search(pattern,line) is not None]

    return url,stockNO,name,commonNames,alleleNames

page=r.get(ai32)

#matches=[re.search(b'meta',line).string.decode('utf-8')+'\n' for line in lines if re.search(b'meta',line) is not None]
#stock=b"jax:strain:sp:StockNo"

#pattern=b'meta'+OR+b'title'


NAME=[re.search(name,m).string for m in matches if re.search(name,m) is not None][0]
stockNO=[re.search(stock,m).string for m in matches if re.search(stock,m) is not None][0]
commonName=[re.search(common,m).string for m in matches if re.search(common,m) is not None][0]
alleleName=[re.search(allele,m).string for m in matches if re.search(allele,m) is not None][0]

title=b'%'
content=b'content="(.+)"'
n=re.search(title,NAME).group(1)
s=re.search(content,stockNO).group(1)
c=re.search(content,commonName).group(1)
a=re.search(content,alleleName).group(1)




#print(''.join(matches))
print(matches)


