import { useEffect, useRef, useState } from 'react';
import { scanBarcode } from '../utils/barcode';
import './CameraViewport.css';

interface CameraViewportProps {
  size?: number;
  onDetect: (payload: string) => void;
}

export default function CameraViewport({ size = 360, onDetect }: CameraViewportProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timer: number;
    let active = true;

    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }

        const tick = async () => {
          if (!active || !videoRef.current) return;
          const payload = await scanBarcode(videoRef.current);
          if (payload) {
            onDetect(payload);
          }
          timer = window.setTimeout(tick, 250);
        };

        tick();
      } catch (err: any) {
        setError(err.message || 'camera error');
      }
    };

    start();

    return () => {
      active = false;
      if (timer) window.clearTimeout(timer);
      const stream = videoRef.current?.srcObject as MediaStream | undefined;
      stream?.getTracks().forEach(t => t.stop());
    };
  }, [onDetect]);

  return (
    <div className="camera-wrap" style={{ width: size, height: size }}>
      <video ref={videoRef} muted playsInline />
      <div className="scan-box" />
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
