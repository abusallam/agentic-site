import fs from 'fs'
import path from 'path'
import sharp from 'sharp'

const fsPromises = fs.promises;

const optimizeImages = async (dir: string) => {
  const files = await fsPromises.readdir(dir);

  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = await fsPromises.lstat(filePath);

    if (stat.isDirectory()) {
      await optimizeImages(filePath);
    } else if (/\.(jpg|jpeg|png)$/.test(filePath)) {
      const optimizedFilePath = filePath.replace(/\.(jpg|jpeg|png)$/, '.webp');
      await sharp(filePath)
        .webp({ quality: 80 })
        .toFile(optimizedFilePath);
      console.log(`Optimized ${filePath} to ${optimizedFilePath}`);
    }
  }
};

optimizeImages(path.join(process.cwd(), 'public')).catch(console.error);
