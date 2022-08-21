output = []
with open('setup.cfg','r') as fp:
    lines = fp.readlines()
    for line in lines:
        if line.startswith('version ='):
            parts = line.split('.')
            currentPatchVersion = int(parts[-1].strip())

            output.append('.'.join(parts[:-1])+'.'+str(currentPatchVersion+1)+'\n')
        else:
            output.append(line)

with open('setup.cfg','w+') as fp:
    fp.writelines(output)