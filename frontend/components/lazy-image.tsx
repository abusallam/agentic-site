import Image from 'next/image';
import { useState, useEffect } from 'react';

interface LazyImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  className?: string;
}

const LazyImage: React.FC<LazyImageProps> = ({ src, alt, width, height, className }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const img = new (window as any).Image();
    img.src = src;
    img.onload = () => setIsLoaded(true);
  }, [src]);

  return (
    <div className={`${className} ${isLoaded ? '' : 'animate-pulse bg-gray-300'}`} style={{ width, height }}>
      {isLoaded && <Image src={src} alt={alt} width={width} height={height} className={className} />}
    </div>
  );
};

export default LazyImage;
