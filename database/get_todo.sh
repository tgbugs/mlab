grep -n '#FIXME' *.py | sed 's/\(.\+:\).\+#/\1\t/' &&
grep -n '#TODO' *.py | sed 's/\(.\+:\).\+#/\1\t/'

