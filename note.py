import sys

msg = '# '+' '.join(sys.argv[1:])

print(':'+msg+':')

with open('/media/pi/616F-8050/root.txt','a') as f:
    f.write(msg+'\n')