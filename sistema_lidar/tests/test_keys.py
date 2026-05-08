import cv2
import numpy as np
img = np.zeros((200,400,3), dtype=np.uint8)
cv2.putText(img, 'Presiona flechas', (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
cv2.imshow('test', img)
while True:
    k = cv2.waitKeyEx(0)
    print(f'Tecla: {k}')
    if k == ord('q'):
        break
cv2.destroyAllWindows()