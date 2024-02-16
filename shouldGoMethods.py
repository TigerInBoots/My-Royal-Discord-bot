def shouldGoFalse(messageGuild):
    shouldGoFile = open("shouldGo.txt", "r+")
    shouldGoFileLines = shouldGoFile.readlines()
    for number, shouldGoFileLine in enumerate(shouldGoFileLines):
        splitLine = shouldGoFileLine.split(";")
        if int(splitLine[1][:-1:]) == int(messageGuild):
            lineNum = number
            shouldGoFile.seek(0)
            shouldGoFile.truncate()
            for num, line in enumerate(shouldGoFileLines):
                if num == lineNum:
                    shouldGoFile.write("False;" + str(messageGuild) + "\n")
                else:
                    shouldGoFile.write(line)
            shouldGoFile.close()
    shouldGoFile.close()

def shouldGoTrue(messageGuild):
    shouldGoFile = open("shouldGo.txt", "r+")
    shouldGoFileLines = shouldGoFile.readlines()
    for number, shouldGoFileLine in enumerate(shouldGoFileLines):
        splitLine = shouldGoFileLine.split(";")
        if int(splitLine[1][:-1:]) == int(messageGuild):
            lineNum = number
            shouldGoFile.seek(0)
            shouldGoFile.truncate()
            for num, line in enumerate(shouldGoFileLines):
                if num == lineNum:
                    shouldGoFile.write("True;" + str(messageGuild) + "\n")
                else:
                    shouldGoFile.write(line)
            shouldGoFile.close()
    shouldGoFile.close()