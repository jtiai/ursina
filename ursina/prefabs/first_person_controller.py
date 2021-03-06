from ursina import *


class FirstPersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5

        self.camera_pivot = Entity(parent=self, y=2)
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)

        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        self.target_smoothing = 100
        self.smoothing = self.target_smoothing

        self.grounded = False
        self.jump_height = 2
        self.jump_duration = .5
        self.jumping = False
        self.air_time = 0

        # self.sphere = Entity(parent=self, collider='sphere', scale=.5, y=.5, model='sphere')


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.y += held_keys['e']
        self.y -= held_keys['q']

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        # self.sphere.x = (held_keys['d'] - held_keys['a']) * self.speed * time.dt
        # self.sphere.z = (held_keys['w'] - held_keys['s']) * self.speed * time.dt
        origin = self.world_position + (self.up*.5) + (self.direction/2)
        hit_info = raycast(origin , self.direction, ignore=[self,], distance=.25, debug=False)
        # hit_info = self.sphere.intersects()
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt
        else:
            # print(hit_info.world_point)
            if hit_info.world_normal.y > .7:
                self.world_position = lerp(self.world_position, hit_info.world_point, time.dt*4)
                return


        # # gravity
        ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,), thickness=.9)

        if ray.distance <= 2:
            if not self.grounded:
                self.land()
            self.grounded = True
            return
        else:
            self.grounded = False

        # if not on ground and not on way up in jump, fall
        self.y -= min(self.air_time, ray.distance-.05)
        self.air_time += time.dt*.25


    def input(self, key):
        if key == 'space':
            self.jump()


    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_duration, resolution=120, curve=curve.out_expo)
        invoke(self.start_fall, delay=self.jump_duration)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True


if __name__ == '__main__':
    from ursina.prefabs.first_person_controller import FirstPersonController
    # window.vsync = False
    app = Ursina()
    Sky(color=color.gray)
    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
    e = Entity(model='cube', scale=(1,5,10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(model='cube', scale=(1,5,10), x=-2, y=.01, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)

    player = FirstPersonController(y=1)
    # camera.z = -10
    player.gun = None

    gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
    gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))

    gun_2 = duplicate(gun, z=7, x=8)
    slope = Entity(model='cube', collider='box', position=(0,0,8), scale=6, rotation=(45,0,0), texture='brick', texture_scale=(8,8))
    slope = Entity(model='cube', collider='box', position=(5,0,10), scale=6, rotation=(80,0,0), texture='brick', texture_scale=(8,8))
    # hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='sphere', color=color.green)
    hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='mesh', color=color.green)
    from ursina.shaders import basic_lighting_shader
    for e in scene.entities:
        e.shader = basic_lighting_shader

    def input(key):
        if key == 'left mouse down' and player.gun:
            gun.blink(color.orange)
            bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+(bullet.forward*50), curve=curve.linear, duration=1)
            destroy(bullet, delay=1)


    # Entity(model='cube', color=color.dark_gray, scale=(9,4,9), y=-.5, collider='box')
    app.run()
