#tests some reqeusts

import requests as r
import re

ai32='http://jaxmice.jax.org/strain/012569.html'
gin='http://jaxmice.jax.org/strain/003718.html'

page=r.get(gin)
lines=page.iter_lines()
page.close()

#matches=[re.search(b'meta',line).string.decode('utf-8')+'\n' for line in lines if re.search(b'meta',line) is not None]
name=b"\<title\>JAX\ Mice\ Database"
stock=b"jax:strain:sp:StockNo"
common=b"jax:strain:sp:StrainCommonNames"
allele=b"jax:strain.sp:AlleleCommonNames"
OR=b"|"

pattern=name+OR+stock+OR+common+OR+allele
#pattern=b'meta'+OR+b'title'

matches=[re.search(pattern,line).string for line in lines if re.search(pattern,line) is not None]

#print(''.join(matches))
print(matches)


