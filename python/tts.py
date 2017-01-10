# test to speech
#!/bin/bash

string=$@
echo $string

speech=${string%>*}
speech=${speech#*en}

echo $speech

espeak -v en-uk-rp -p 99 -s 180 -k20 "$speech" 1>>/dev/shm/voice.log 2>>/dev/shm/voice.log