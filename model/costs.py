from PIL import Image
from model import config, logging, cards
from csv import DictReader

TEMPLES = config["temples"]

def get_temple_variant(image, temple):
    if temple not in TEMPLES:
        raise ValueError(f"'{temple}' is not a valid temple.")
    width, height = image.size
    version_height = height // len(TEMPLES)
    version_index = TEMPLES.index(temple)
    top = version_index * version_height
    bottom = (version_index + 1) * version_height
    return image.crop((0, top, width, bottom))

def change_cost_color(image, temple, tier=""):
    if temple not in TEMPLES:
        raise ValueError(f"'{temple}' is not a valid temple.")
    for x in range(image.width):
        for y in range(image.height):
            if [temple] == "Structure":
                if [tier] == "Rare" or [tier] == "Talking":
                    current_pixel = image.getpixel((x, y))[:3]
                    if current_pixel == (190, 117, 65):
                        image.putpixel((x, y), config["light_tone_golden"][temple])
                    elif current_pixel == (125, 78, 48):
                        image.putpixel((x, y), config["text_colors_golden"][temple])
                    elif current_pixel == (78, 50, 38):
                        image.putpixel((x, y), config["dark_tone_golden"][temple])
                    elif current_pixel == (64, 42, 33):
                        image.putpixel((x, y), config["darker_tone_golden"][temple])
                else:
                    current_pixel = image.getpixel((x, y))[:3]
                    if current_pixel == (190, 117, 65):
                        image.putpixel((x, y), config["light_tone_normal"][temple])
                    elif current_pixel == (125, 78, 48):
                        image.putpixel((x, y), config["text_colors_normal"][temple])
                    elif current_pixel == (78, 50, 38):
                        image.putpixel((x, y), config["dark_tone_normal"][temple])
                    elif current_pixel == (64, 42, 33):
                        image.putpixel((x, y), config["darker_tone_normal"][temple])
            else:
                current_pixel = image.getpixel((x, y))[:3]
                if current_pixel == (190, 117, 65):
                    image.putpixel((x, y), config["light_tone"][temple])
                elif current_pixel == (125, 78, 48):
                    image.putpixel((x, y), config["text_colors"][temple])
                elif current_pixel == (78, 50, 38):
                    image.putpixel((x, y), config["dark_tone"][temple])
                elif current_pixel == (64, 42, 33):
                    image.putpixel((x, y), config["darker_tone"][temple])
    return image

class Blood:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Blood:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Blood(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Blood:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Blood(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        img = Image.open(f"assets/costs/blood/blood.png").convert("RGBA")
        cost_img = change_cost_color(img, temple)
        total_width = cost_img.width * self.amount
        final_img = Image.new('RGBA', (total_width, cost_img.height))
        for i in range(self.amount):
            x_offset = i * cost_img.width
            final_img.paste(cost_img, (x_offset, 0))
        return final_img

class Bones:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Bones:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Bones(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Bones:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Bones(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 4:
            img = Image.open(f"assets/costs/bones/bones{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/bones/bones.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image

class Energy:
    def __init__(self, energy: int = 0, overcharge: int = 0, overheat: int = 0, renew: int = 0, reroute: int = 0, shortage: int = 0):
        self.energy = energy
        self.overcharge = overcharge
        self.overheat = overheat
        self.renew = renew
        self.reroute = reroute
        self.shortage = shortage

    def __add__(self, other):
        if type(other) is not Energy:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Energy(self.energy + other.energy, self.overcharge + other.overcharge, self.overheat + other.overheat, self.renew + other.renew, self.reroute + other.reroute, self.shortage + other.shortage)

    def __sub__(self, other):
        if type(other) is not Energy:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Energy(self.energy - other.energy, self.overcharge - other.overcharge, self.overheat - other.overheat, self.renew - other.renew, self.reroute - other.reroute, self.shortage - other.shortage)

    def getCostImage(self, temple: str) -> Image:
        first_cell = change_cost_color(Image.open(f"assets/costs/cell_first.png"), temple)
        cell = change_cost_color(Image.open(f"assets/costs/cell.png"), temple)

        def paste_cell(bar, cell_content, first=False):
            nonlocal x_offset
            bar.paste(first_cell if first else cell, (x_offset, 0))
            x_offset += 20 * int(first)
            bar.paste(cell_content, (x_offset, 20))
            x_offset += 40

        def generate_bar_image(amount, resource):
            nonlocal x_offset
            if amount > 4:
                if amount >= 10:
                    bar = Image.new("RGBA", (60 + 40 * 3, 90))
                    paste_cell(bar, Image.open(f"assets/costs/energy/{resource}_1.png"), True)
                    paste_cell(bar, Image.open(f"assets/costs/energy/{resource}_{amount - 10}.png"))
                else:
                    bar = Image.new("RGBA", (60 + 40 * 2, 90))
                    paste_cell(bar, Image.open(f"assets/costs/energy/{resource}_{amount}.png"), True)
                paste_cell(bar, Image.open(f"assets/costs/energy/{resource}_x.png"))
                paste_cell(bar, Image.open(f"assets/costs/energy/{resource}.png"))
            else:
                bar = Image.new("RGBA", (60 + 40 * (amount - 1), 90))
                for i in range(amount):
                    paste_cell(bar, Image.open(f"assets/costs/energy/{resource}.png"), i == 0)
            return bar
        final_width = 0
        bars = []
        if self.energy > 0:
            x_offset = 0
            energy_bar = generate_bar_image(self.energy, "energy")
            final_width += energy_bar.width
            bars.append(energy_bar)
        if self.overcharge > 0:
            x_offset = 0
            overcharge_bar = generate_bar_image(self.overcharge, "overcharge")
            final_width += overcharge_bar.width
            bars.append(overcharge_bar)
        if self.overheat > 0:
            x_offset = 0
            overheat_bar = generate_bar_image(self.overheat, "overheat")
            final_width += overheat_bar.width
            bars.append(overheat_bar)
        if self.renew > 0:
            x_offset = 0
            renew_bar = generate_bar_image(self.renew, "renew")
            final_width += renew_bar.width
            bars.append(renew_bar)
        if self.reroute > 0:
            x_offset = 0
            reroute_bar = generate_bar_image(self.reroute, "reroute")
            final_width += reroute_bar.width
            bars.append(reroute_bar)
        if self.shortage > 0:
            x_offset = 0
            shortage_bar = generate_bar_image(self.shortage, "shortage")
            final_width += shortage_bar.width
            bars.append(shortage_bar)
        cost_image = Image.new("RGBA", (final_width, 90))
        cost_image.paste(bars[0])
        width = 0
        for i in range(len(bars)):
            cost_image.paste(bars[i], (width, 0))
            width += bars[i].width
        return cost_image

class Gems:
    def __init__(self, *gems: str):
        self.gems = list(gems)

    def __add__(self, other):
        if type(other) not in [Gems, str]:
            raise TypeError('Add operation between gems may only be done with objects of type Gems or str.')
        self.gems += other.gems if type(other) is Gems else [other]

    def __sub__(self, other):
        if type(other) not in [Gems, str]:
            raise TypeError('Sub operation between gems may only be done with objects of type Gems or str.')
        if type(other) is str:
            other = [other]
        for gem in other:
            if gem in self.gems:
                self.gems.remove(gem)

    def copy(self):
        return Gems(*self.gems[:])

    @staticmethod
    def getGemImage(gem, temple) -> Image:
        shatter = "shattered_" if "shattered" in gem else ""
        gem = gem.split(" ")[-1].lower()
        color = dict(emeralds="emerald", sapphires="sapphire", rubies="ruby", topazes="topaz", amethysts="amethyst", garnets="garnet", onyxs="onyx", prisms="prism").get(gem, gem)
        img = Image.open(f"assets/costs/gems/{shatter}{color.lower()}.png").convert("RGBA")
        return change_cost_color(img, temple)

    def getCostImage(self, temple: str) -> Image:
        gem_images = []
        for gem in self.gems:
            image = self.getGemImage(gem, temple)
            for _ in range(int(gem.split(" ")[0])):
                gem_images.append(image)
        total_width = sum(img.width for img in gem_images) - (len(gem_images) - 1) * 10
        max_height = max(img.height for img in gem_images)
        cost_image = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
        offset = 0
        for img in gem_images:
            if img.height == 90 and img.height != max_height:
                paste_position = (offset, 10)
            else:
                paste_position = (offset, 0)
            cost_image.paste(img, paste_position, mask=img)
            offset += img.width - 10
        return cost_image

class Alchemy:
    def __init__(self, *chemicals: str):
        self.chemicals = list(chemicals)

    def __add__(self, other):
        if type(other) not in [Alchemy, str]:
            raise TypeError('Add operation between chemicals may only be done with objects of type Chemicals or str.')
        self.chemicals += other.chemicals if type(other) is Alchemy else [other]

    def __sub__(self, other):
        if type(other) not in [Alchemy, str]:
            raise TypeError('Sub operation between chemicals may only be done with objects of type Chemicals or str.')
        if type(other) is str:
            other = [other]
        for gem in other:
            if gem in self.chemicals:
                self.chemicals.remove(gem)

    def copy(self):
        return Alchemy(*self.chemicals[:])

    def getCostImage(self, temple: str) -> Image:
        chemical_images = []
        for chemical in self.chemicals:
            name = chemical.split(" ")[-1].lower()
            image = Image.open(f"assets/costs/alchemy/{name}.png").convert("RGBA")
            for _ in range(int(chemical.split(" ")[0])):
                chemical_images.append(image)
        space_removed = {1: 0, 2: 0, 3: 0, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 5}.get(len(chemical_images), 6) * 10
        total_width = (sum(img.width + 10 - space_removed for img in chemical_images) - 10 + space_removed)
        cost_image = Image.new("RGBA", (total_width, 100), (255, 255, 255, 0))
        offset = 0
        for img in chemical_images:
            cost_image.paste(img, (offset, 0), mask=img)
            offset += img.width + 10 - space_removed
        return cost_image
    
class Blackout:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Blackout:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Blackout(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Blackout:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Blackout(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        baseImage = Image.open("assets/costs/blackout_bar.png").convert("RGBA")
        newBaseImage = change_cost_color(baseImage, temple)
        if self.amount > 0:
            i = self.amount
            pos1 = round(i%10)
            pastepos1 = (130, 10)
            i = i/10
            pos2 = round(i%10)
            pastepos2 = (70, 10)
            i = i/10
            pos3 = round(i)
            pastepos3 = (10, 10)
            pos1Image = Image.open(f"assets/costs/blackout/blackout_{str(pos1)}.png").convert("RGBA")
            newPos1Image = change_cost_color(pos1Image, temple)
            pos2Image = Image.open(f"assets/costs/blackout/blackout_{str(pos2)}.png").convert("RGBA")
            newPos2Image = change_cost_color(pos2Image, temple)
            pos3Image = Image.open(f"assets/costs/blackout/blackout_{str(pos3)}.png").convert("RGBA")
            newPos3Image = change_cost_color(pos3Image, temple)
            if pos1 != 0:
                newBaseImage.paste(newPos1Image, pastepos1, newPos1Image)
            if pos2 != 0:
                newBaseImage.paste(newPos2Image, pastepos2, newPos2Image)
            if pos3 != 0:
                newBaseImage.paste(newPos3Image, pastepos3, newPos3Image)
        final_image = newBaseImage
        return final_image
        
class Skulls:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Skulls:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Skulls(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Skulls:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Skulls(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 4:
            img = Image.open(f"assets/costs/skulls/skull_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/skulls/skull.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Sun:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Sun:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Sun(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Sun:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Sun(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/sun/sun_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/sun/sun.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Frequency:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Frequency:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Frequency(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Frequency:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Frequency(self.amount - other.amount)
    
    def getCostImage(self, temple: str) -> Image:
        baseImage = Image.open("assets/costs/frequency_bar.png").convert("RGBA")
        newBaseImage = change_cost_color(baseImage, temple)
        if self.amount > 0:
            i = round(self.amount)
            pos1 = round(i%10)
            pastepos1 = (250, 10)
            i = round(i/10)
            pos2 = round(i%10)
            pastepos2 = (170, 10)
            i = round(i/10)
            pos3 = round(i%10)
            pastepos3 = (90, 10)
            i = round(i/10)
            pos4 = round(i%10)
            pastepos4 = (10, 10)
            pos1Image = Image.open(f"assets/costs/frequency/frequency_{str(pos1)}.png").convert("RGBA")
            pos2Image = Image.open(f"assets/costs/frequency/frequency_{str(pos2)}.png").convert("RGBA")
            pos3Image = Image.open(f"assets/costs/frequency/frequency_{str(pos3)}.png").convert("RGBA")
            pos4Image = Image.open(f"assets/costs/frequency/frequency_{str(pos4)}.png").convert("RGBA")
            if 6 > pos1 != 0 :
                newBaseImage.paste(pos1Image, pastepos1, pos1Image)
            if 6 > pos2 != 0:
                newBaseImage.paste(pos2Image, pastepos2, pos2Image)
            if 6 > pos3 != 0:
                newBaseImage.paste(pos3Image, pastepos3, pos3Image)
            if 6 > pos4 != 0:
                newBaseImage.paste(pos4Image, pastepos4, pos4Image)
        final_image = newBaseImage
        return final_image

class Teeth:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Teeth:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Teeth(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Teeth:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Teeth(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/teeth/teeth_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/teeth/tooth.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Bile:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Bile:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Bile(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Bile:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Bile(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/bile/bile_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/bile/bile.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Truth:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Truth:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Truth(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Truth:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Truth(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/truth&lies/truth_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/truth&lies/truth.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Lies:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Lies:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Lies(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Lies:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Lies(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/truth&lies/lies_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/truth&lies/lie.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Seeds:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Seeds:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Seeds(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Seeds:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Seeds(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/seeds/seeds_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/seeds/seed.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Stardust:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Stardust:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Stardust(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Stardust:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Stardust(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/stardust/stardust_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/stardust/stardust.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Gasoline:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Gasoline:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Gasoline(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Gasoline:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Gasoline(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/gasoline/gasoline_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/gasoline/gasoline.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image

class Ash:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Ash:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Ash(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Ash:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Ash(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/ash/ash_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/ash/ash.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image
    
class Coral:
    def __init__(self, amount: int):
        self.amount = amount

    def __add__(self, other):
        if type(other) is not Coral:
            raise TypeError("Add operation can only be performed on two resources of the same type")
        return Coral(self.amount + other.amount)

    def __sub__(self, other):
        if type(other) is not Coral:
            raise TypeError("Sub operation can only be performed on two resources of the same type")
        return Coral(self.amount - other.amount)

    def getCostImage(self, temple: str) -> Image:
        if self.amount > 3:
            img = Image.open(f"assets/costs/coral/coral_{self.amount}.png").convert("RGBA")
            return change_cost_color(img, temple)
        img = Image.open("assets/costs/coral/coral.png").convert("RGBA")
        version_img = change_cost_color(img, temple)
        duplicate_image = version_img.copy()
        final_width = version_img.width + (duplicate_image.width - 10) * (self.amount - 1)
        final_image = Image.new('RGBA', (final_width, version_img.height))
        final_image.paste(version_img, (0, 0))
        for i in range(self.amount - 1):
            paste_position = (version_img.width + (duplicate_image.width - 10) * i - 10, 0)
            final_image.paste(duplicate_image, paste_position, duplicate_image)
        return final_image

def get_cost(strcost):
    cost = []
    if strcost is None:
        return cost
    try:
        for c in strcost.split(" + "):
            if "blood" in c:
                cost.append(Blood(int(c.split(" ")[0])))
            elif "bone" in c or "bones" in c:
                cost.append(Bones(int(c.split(" ")[0])))
            elif "energy" in c or "overcharge" in c or "overheat" in c or "renew" in c or "reroute" in c or "shortage" in c:
                energy = None
                i = 0
                while energy is None and i < len(cost):
                    if isinstance(cost[i], Energy):
                        energy = cost[i]
                if "energy" in c:  # Blue Energy
                    if energy:
                        energy.energy = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(energy=int(c.split(" ")[0])))
                elif "overcharge" in c:  # Yellow Energy
                    if energy:
                        energy.overcharge = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(overcharge=int(c.split(" ")[0])))
                elif "overheat" in c:  # Red Energy
                    if energy:
                        energy.overheat = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(overheat=int(c.split(" ")[0])))
                elif "renew" in c:  # Green Energy
                    if energy:
                        energy.renew = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(renew=int(c.split(" ")[0])))
                elif "reroute" in c:  # Orange Energy
                    if energy:
                        energy.reroute = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(reroute=int(c.split(" ")[0])))
                elif "shortage" in c:  # Purple Energy
                    if energy:
                        energy.shortage = int(c.split(" ")[0])
                    else:
                        cost.append(Energy(shortage=int(c.split(" ")[0])))
            elif any(gem in c for gem in
                     ["emerald", "sapphire", "ruby", "rubies", "topaz", "amethyst", "garnet", "onyx", "prism"]):
                gems = None
                i = 0
                while gems is None and i < len(cost):
                    if isinstance(cost[i], Gems):
                        gems = cost[i]
                    i += 1
                if gems:
                    gems += c
                else:
                    gems = Gems(c)
                    cost.append(gems)
            elif any(chemical in c for chemical in ["flesh", "metal", "elixir", "aether"]):
                chemicals = None
                i = 0
                while chemicals is None and i < len(cost):
                    if isinstance(cost[i], Alchemy):
                        chemicals = cost[i]
                    i += 1
                if chemicals:
                    chemicals += c
                else:
                    chemicals = Alchemy(c)
                    cost.append(chemicals)
            elif "blackout" in c:
                cost.append(Blackout(int(c.split(" ")[0])))
            elif "skulls" in c or "skull" in c:
                cost.append(Skulls(int(c.split(" ")[0])))
            elif "sun" in c:
                cost.append(Sun(int(c.split(" ")[0])))
            elif "frequency" in c:
                cost.append(Frequency(int(c.split(" ")[0])))
            elif "teeth" in c or "tooth" in c:
                cost.append(Teeth(int(c.split(" ")[0])))
            elif "bile" in c:
                cost.append(Bile(int(c.split(" ")[0])))
            elif "truth" in c:
                cost.append(Truth(int(c.split(" ")[0])))
            elif "lie" in c or "lies" in c:
                cost.append(Lies(int(c.split(" ")[0])))
            elif "seed" in c or "seeds" in c:
                cost.append(Seeds(int(c.split(" ")[0])))
            elif "stardust" in c:
                cost.append(Stardust(int(c.split(" ")[0])))
            elif "gasoline" in c:
                cost.append(Gasoline(int(c.split(" ")[0])))
            elif "ash" in c:
                cost.append(Ash(int(c.split(" ")[0])))
            elif "coral" in c:
                cost.append(Coral(int(c.split(" ")[0])))
            # Add custom costs here with other elif
            else:
                raise KeyError(f"Unknown cost type: {c}")
        return cost
    except KeyError as e:
        print(f"Error: {e}")
        logging.error(f"Error: {e}")
