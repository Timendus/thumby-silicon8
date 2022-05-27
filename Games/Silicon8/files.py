def loadinto(filename, memory):
    try:
        file = open(filename, 'rb')
        file.seek(0,2)
        size = file.tell()
        if size > len(memory):
            return -1
        file.seek(0)
        file.readinto(memory)
        return size
    except Exception as err:
        print('Could not read CH8 file ' + filename + ':', err)
