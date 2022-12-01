import os 
src = './docs/mm2r/数据/tasks'
dst = './docs/mm2r/数据/支线任务'
if __name__ == '__main__':
  for name in os.listdir(src):
    print(name)
    if name.startswith('任务名'):
      os.rename(os.path.join(src, name), os.path.join(dst, name[4:]))
    else:
      os.rename(os.path.join(src, name), os.path.join(dst, name))