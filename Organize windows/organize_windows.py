import subprocess
import win32gui, win32con, win32process, win32api
import time, os

pathes = []
config = {
    'height' : 850,
    'l_justify' : 600,
    'r_justify' : 0,
    'between' : 0,
    }

def retrieve_config():
    file_config = open(os.path.join(os.getcwd(),'config.txt'), 'r')
    global pathes
    global config
    part = 1
    for line in file_config:
        if part == 1:
            if line[0] == "#":
                part = 2
                continue
            if line.strip() != '':
                pathes += [os.path.normpath(line.strip('\n'))]
        if part == 2:
            if line.strip() != '':
                l = line.replace(' ','').strip('\n')
                key, value = l[:l.find(':')], l[l.find(':')+1:]
                config[key] = int(value)
        
    

def get_rec_between(between_):
    w_width = win32api.GetSystemMetrics(win32con.SM_CXMINIMIZED)
    desktop = win32gui.GetDesktopWindow()
    d_x, d_y, d_width, d_height = win32gui.GetWindowRect(desktop)
    total_count_wnds = len(pathes)
    recommended_between = int(((d_width-config['l_justify']-config['r_justify'])-(total_count_wnds*w_width))/(total_count_wnds-1))
    return recommended_between if config['between'] > recommended_between else between_

def get_width():
    desktop = win32gui.GetDesktopWindow()
    d_x, d_y, d_width, d_height = win32gui.GetWindowRect(desktop)
    total_count_wnds = len(pathes)
    between_ = get_rec_between(config['between'])
    return int(((d_width-config['l_justify']-config['r_justify'])-((total_count_wnds-1)*between_))/(total_count_wnds))
               
class set_pos_and_size:
    counter = -1
    
    def __new__(cls, *args, **kwargs):
        cls.counter += 1
        return super().__new__(cls)
    
    def __init__(self, hwnd):
        self.hwnd = hwnd
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        self.x, self.y = (get_width()+get_rec_between(config['between']))*self.counter + config['l_justify'], 0
        print('hwnd:', hwnd)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, self.x, self.y, get_width(), config['height'], win32con.SWP_SHOWWINDOW)        

def get_hwnds_for_pid():
  def callback (hwnd, hwnds):
    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        hwnds.append(hwnd)
    return True
    
  hwnds = []
  win32gui.EnumWindows(callback, hwnds)
  return hwnds

def wait_until(func, args, timeout):
    n = timeout*2
    for i in range(n):
        res = func(*args)
        if res != 0:
            return func(*args)
        else:
            time.sleep(0.5)
        
    
        

def main():
    retrieve_config()
    for path in pathes:
        dir_name = "{}".format(path.split('\\')[-1])
        print(dir_name)
        hwnd = win32gui.FindWindow(None, dir_name)
        print(hwnd)
        if hwnd:
            set_pos_and_size(hwnd)
        else:
            process = subprocess.Popen('explorer /separate, "{}"'.format(path))
            hwnd = wait_until(win32gui.FindWindow, (None, dir_name), timeout = 10)
            set_pos_and_size(hwnd)
         

if __name__ == "__main__":
    main()
