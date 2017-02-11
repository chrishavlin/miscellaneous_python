"""
automates the process of re-sizing an image to meet an image size requirement.
Uses Pillow to resize an image to desingated target size. Some notes:
(1) image size here is the uncompressed image size: width pixels * height pixels * bytes_per_pixels
(2) preserves exif data 
(3) ONLY works on JPG's for now 
(4) uses bicubic interpoloation for re-sizing (easily changed, search for BICUBIC)

IMPORTANT: this software resizes without any regard to initial quality of your photos. If you try 
to resize a photo with initially low resolution you will get a crappy resized photo.  

Copyright (C) 2016  Chris Havlin, <https://chrishavlin.wordpress.com>, @s_i_r_h_c
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from PIL import Image
import os,sys

class img:
    def __init__(self,impath):
        self.file=impath
        self.colordepth,self.fmt=self.bytes_per_pixel()
        self.im=Image.open(self.file)

    def size(self):
        """ 
            pulls out measurements of size: 
                (width in px, height in px, # of px, aspect ratio, image size in Mb)
            image size = pixels * bytes_per_pixel / 1e6
        """
        wid=self.im.size[0]
        ht=self.im.size[1]
        pixels=wid*ht
        aspect = float(wid) / float(ht)
        Mb = pixels * self.colordepth / 1e6
        return wid,ht,pixels,aspect,Mb
    
    def bytes_per_pixel(self):
        """ sets the colordepth (bytes per pixel)"""
        ext = self.file.split('.')[-1] # file extension
        if ext.lower() == 'jpg':
        # JPG has 3 color channels for RGB, 8 bit per channel = 24 bits= 3 bytes
           colordepth = 3.0
           fmt='JPEG' 
        else:
           print 'color depth (bytes/pixel) unknown for file type ' + ext
        return colordepth,fmt

    def resize_to_targ(self,targ=50.,min_targ=49.,max_targ=51.):
        """ 
           resizes to a target UNCOMPRESSED image size
           min_targ = min image size 
           max_targ = max image size 
        """
        if self.size()[4] < min_targ or self.size()[4] > max_targ:
           rat = float(self.size()[3])
           new_ht=int((targ*1e6 / self.colordepth / rat)**0.5)
           new_wd=int(new_ht * self.size()[3])
           print('resizing '+ self.file +' from ' + str(round(self.size()[4],2)) + ' Mb ' + 
                 str((self.size()[0],self.size()[1])) + ' to ' + str(targ) + ' Mb ' + str((new_wd,new_ht)))
           new_image=self.im.resize((new_wd,new_ht),resample=Image.BICUBIC)
        else:
           new_image = self.im

        return new_image

def check_dir(imdir,reproc=False):
    print imdir
    absdir=os.path.abspath(imdir)
    for fn in os.listdir(absdir):
        fl=imdir+'/'+fn
        newfl=fn.split('.')[0]+'_qcd.'+ fn.split('.')[1]
        newpath=imdir + '/' +newfl 
        if(os.path.isfile(fl) and fn.lower().split('.')[1]=='jpg' and 'qcd' not in fn 
           and os.path.isfile(newpath)==reproc):
           im = img(fl) 
           new_im = im.resize_to_targ()
           new_im.save(newpath,format=im.fmt, subsampling=0, quality=100,exif=im.im.info['exif'])

if __name__=='__main__':
    check_dir(sys.argv[1],True)
   
