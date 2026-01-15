from PIL import Image, ImageDraw
import random
import os

def create_sample_images_pil():
    width, height = 1000, 1000
    
    # OP1: Brown-ish
    op1 = Image.new('RGB', (width, height), color=(120, 90, 60))
    d1 = ImageDraw.Draw(op1)
    
    # Draw Pits
    pits = []
    rows, cols = 5, 5
    sp_x = width // (cols + 1)
    sp_y = height // (rows + 1)
    
    for i in range(rows):
        for j in range(cols):
            x = (j + 1) * sp_x
            y = (i + 1) * sp_y
            r = 20
            # Draw pit (dark circle)
            d1.ellipse([x-r, y-r, x+r, y+r], fill=(80, 50, 30), outline=(60, 40, 20))
            pits.append((x, y))

    op1.save("sample_op1.png")
    print("Created sample_op1.png (using PIL)")

    # OP3: Same base + Plants
    op3 = op1.copy()
    d3 = ImageDraw.Draw(op3)
    
    for (x, y) in pits:
        # 80% survival
        if random.random() < 0.8:
            # Green plant
            r = random.randint(15, 25)
            d3.ellipse([x-r, y-r, x+r, y+r], fill=(50, 200, 50))
            d3.ellipse([x-10, y-10, x+10, y+10], fill=(100, 255, 100))
        else:
            # Dead (Empty or brown spot)
            if random.random() > 0.5:
                 d3.ellipse([x-5, y-5, x+5, y+5], fill=(100, 100, 50))

    op3.save("sample_op3.png")
    print("Created sample_op3.png (using PIL)")

if __name__ == "__main__":
    create_sample_images_pil()
