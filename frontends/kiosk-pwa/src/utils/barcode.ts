import type { Result } from '@zxing/library';

let detector: BarcodeDetector | null = null;
try {
  detector = new BarcodeDetector({ formats: ['qr_code'] });
} catch {
  detector = null;
}

let zxingReader: any;

export async function scanBarcode(video: HTMLVideoElement): Promise<string | null> {
  if (detector) {
    try {
      const codes = await detector.detect(video);
      if (codes.length > 0) {
        return codes[0].rawValue || null;
      }
    } catch {
      // ignore
    }
  }

  try {
    if (!zxingReader) {
      const { BrowserMultiFormatReader } = await import('@zxing/library');
      zxingReader = new BrowserMultiFormatReader();
    }
    const result: Result = await zxingReader.decodeFromVideoElement(video);
    return result.getText();
  } catch {
    return null;
  }
}
