class Memory(BoxLayout):
    bits = Estimator(0, 128, 0.1)
    differs = False
    next_differs = False
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        hasher = get_hasher()
        nbits = self.bits.median()
        print 'nbits', nbits
        frac = 1 - 0.5**(1.0/nbits)
        print 'nbits', nbits, 'frac', frac
        rnd = VisualHash.BitTweakedRandom(self.original.text,frac, self.img.num,self.img.num)
        self.next_differs = True
        self.img.num += 1
        if VisualHash.StrongRandom(self.original.text+'hi'+str(self.img.num)).random() < 0.25:
            self.next_differs = False
            rnd = VisualHash.StrongRandom(self.original.text)
        NextImage(self.img, image_size, lambda: rnd, hasher)
    def on_select(self, *args):
        self.bits = Estimator(0, 128, 0.1)
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.original.x = 0
        self.img.x = self.width
        hasher = get_hasher()
        self.original.text = '%08d' % SystemRandom().randrange(0, 10**8)
        rnd = VisualHash.StrongRandom(self.original.text)
        self.img.x = self.width
        NextImage(self.original, image_size, lambda: rnd, hasher)
        self.img.x = self.width
        self.begin_next_img()
        self.img.x = self.width
        self.Reset()
    def Reset(self):
        self.entropy_label.text = 'Entropy:  %.1f' % self.bits.median()
        if self.original.have_next:
            self.differs = self.next_differs
            im = self.original.next[0]
            self.original.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.original.texture = texture
        else:
            Clock.schedule_once(lambda dt: self.Reset(), 0.25)
            return
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        anim = Animation(x=self.width, duration=animtime)
        anim.start(self.img)
        anim = Animation(x=0, t='out_back', duration=animtime)
        anim.start(self.original)
    def Start(self):
        if self.img.have_next:
            im = self.img.next[0]
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img.texture = texture
            self.begin_next_img()
        else:
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        self.left_button.disabled = False
        self.right_button.text = 'Same'
        anim = Animation(x=0, t='out_back', duration=animtime)
        anim.start(self.img)
        anim = Animation(x=-self.width, duration=animtime)
        anim.start(self.original)
    def ItMatches(self):
        print 'same:', self.differs, self.img.current_im != self.original.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), False)
            print 'new bits:', self.bits.median()
        else:
            print 'Nice!'
        self.Reset()
    def ItDiffers(self):
        print 'differs:', self.differs, self.img.current_im != self.original.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), True)
            print 'new bits:', self.bits.median()
        else:
            print 'Oops!'
        self.Reset()

