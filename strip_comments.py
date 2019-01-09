import sys

with open(sys.argv[1]) as f:
    with open(sys.argv[2], 'w') as f2:
        for line in f.readlines():
            line_newlines = line
            line = line.strip()
            if line and (line[0] != '/' and line[0] != '*'):
                index = line.find("//")
                line = line[:index] if index + 1 else line
                f2.write(line_newlines.replace("$j", "$").replace("beef.dom", "dom"))
