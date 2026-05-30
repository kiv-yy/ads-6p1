import { useEffect, useRef } from 'react';

const METEOR_COUNT = 28;

function randomBetween(min, max) {
  return min + Math.random() * (max - min);
}

export default function MeteorRain() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const context = canvas.getContext('2d');
    const angle = Math.PI * 0.72;
    const meteors = [];
    let animationFrame = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };

    const createMeteor = () => {
      const length = randomBetween(40, 130);
      const speed = randomBetween(4, 9);
      const colorChoice = Math.random();
      const colors = colorChoice < 0.4
        ? ['#FFE033', 'rgba(255,210,0,0)']
        : colorChoice < 0.75
          ? ['#A8E03A', 'rgba(140,210,20,0)']
          : ['#B8EDE0', 'rgba(150,230,210,0)'];

      const spawnEdge = Math.random();
      const x = spawnEdge < 0.6
        ? randomBetween(canvas.width * 0.1, canvas.width * 1.1)
        : randomBetween(canvas.width * 0.5, canvas.width * 1.2);
      const y = spawnEdge < 0.6
        ? randomBetween(-80, canvas.height * 0.3)
        : randomBetween(-80, canvas.height * 0.6);

      return {
        x,
        y,
        dx: Math.cos(angle) * speed,
        dy: Math.sin(angle) * speed,
        length,
        headColor: colors[0],
        tailColor: colors[1],
        alpha: randomBetween(0.5, 1),
      };
    };

    const seedMeteors = () => {
      meteors.length = 0;
      for (let index = 0; index < METEOR_COUNT; index += 1) {
        const meteor = createMeteor();
        const offset = randomBetween(0, 200);
        meteor.x += meteor.dx * offset;
        meteor.y += meteor.dy * offset;
        meteors.push(meteor);
      }
    };

    const drawBackground = () => {
      const gradient = context.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, '#1E7A55');
      gradient.addColorStop(0.3, '#1A9060');
      gradient.addColorStop(0.6, '#12A86A');
      gradient.addColorStop(1, '#0EB8C0');
      context.fillStyle = gradient;
      context.fillRect(0, 0, canvas.width, canvas.height);

      const glowOne = context.createRadialGradient(canvas.width * 0.72, canvas.height * 0.28, 0, canvas.width * 0.72, canvas.height * 0.28, canvas.width * 0.22);
      glowOne.addColorStop(0, 'rgba(200,255,230,0.18)');
      glowOne.addColorStop(1, 'rgba(200,255,230,0)');
      context.fillStyle = glowOne;
      context.fillRect(0, 0, canvas.width, canvas.height);

      const glowTwo = context.createRadialGradient(canvas.width * 0.2, canvas.height * 0.65, 0, canvas.width * 0.2, canvas.height * 0.65, canvas.width * 0.18);
      glowTwo.addColorStop(0, 'rgba(190,255,200,0.14)');
      glowTwo.addColorStop(1, 'rgba(190,255,200,0)');
      context.fillStyle = glowTwo;
      context.fillRect(0, 0, canvas.width, canvas.height);
    };

    const drawMeteor = (meteor) => {
      const tailX = meteor.x - Math.cos(angle) * meteor.length;
      const tailY = meteor.y - Math.sin(angle) * meteor.length;
      const gradient = context.createLinearGradient(tailX, tailY, meteor.x, meteor.y);
      gradient.addColorStop(0, meteor.tailColor);
      gradient.addColorStop(1, meteor.headColor);

      context.save();
      context.globalAlpha = meteor.alpha;
      context.strokeStyle = gradient;
      context.lineWidth = 3.5;
      context.lineCap = 'round';
      context.beginPath();
      context.moveTo(tailX, tailY);
      context.lineTo(meteor.x, meteor.y);
      context.stroke();
      context.restore();
    };

    const animate = () => {
      drawBackground();
      meteors.forEach((meteor, index) => {
        meteor.x += meteor.dx;
        meteor.y += meteor.dy;

        if (meteor.x < -200 || meteor.y > canvas.height + 100) {
          meteors[index] = createMeteor();
        } else {
          drawMeteor(meteor);
        }
      });
      animationFrame = requestAnimationFrame(animate);
    };

    const resizeObserver = new ResizeObserver(() => {
      resize();
      seedMeteors();
    });

    resize();
    seedMeteors();
    resizeObserver.observe(canvas);
    animate();

    return () => {
      cancelAnimationFrame(animationFrame);
      resizeObserver.disconnect();
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-hidden="true" />;
}
