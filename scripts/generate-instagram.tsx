import { ImageResponse } from '@takumi-rs/image-response';
import { writeFileSync } from 'fs';

async function generateInstagram() {
  // Instagram square format: 1080x1080
  const response = new ImageResponse(
    <div
      style={{
        width: '1080px',
        height: '1080px',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f0f8fc',
        fontFamily: 'system-ui, sans-serif',
        padding: '60px',
        justifyContent: 'space-between',
      }}
    >
      {/* Header Card */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#88d4ee',
          border: '4px solid #000000',
          borderRadius: '10px',
          padding: '40px',
          boxShadow: '8px 8px 0px 0px #000000',
        }}
      >
        <h1
          style={{
            fontSize: '80px',
            fontWeight: 800,
            color: '#000000',
            margin: 0,
            letterSpacing: '-2px',
          }}
        >
          TASKFOLIO
        </h1>
        <p
          style={{
            fontSize: '32px',
            fontWeight: 600,
            color: '#000000',
            margin: '15px 0 0 0',
          }}
        >
          See which tasks AI will automate in your job
        </p>
      </div>

      {/* Stats Row */}
      <div
        style={{
          display: 'flex',
          gap: '30px',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            backgroundColor: '#ffffff',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '25px 40px',
            boxShadow: '5px 5px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '56px', fontWeight: 800, color: '#000000' }}>361</span>
          <span style={{ fontSize: '18px', fontWeight: 600, color: '#000000' }}>OCCUPATIONS</span>
        </div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            backgroundColor: '#ffffff',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '25px 40px',
            boxShadow: '5px 5px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '56px', fontWeight: 800, color: '#000000' }}>6,690</span>
          <span style={{ fontSize: '18px', fontWeight: 600, color: '#000000' }}>TASKS</span>
        </div>
      </div>

      {/* Features */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '15px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            backgroundColor: '#ee8888',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '18px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '28px' }}>⏳</span>
          <span style={{ fontSize: '24px', fontWeight: 700, color: '#000000' }}>Half-Life: When 50% of tasks are AI-affected</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            backgroundColor: '#97ee88',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '18px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '28px' }}>📊</span>
          <span style={{ fontSize: '24px', fontWeight: 700, color: '#000000' }}>Future-Proof Index for every occupation</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            backgroundColor: '#fed170',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '18px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '28px' }}>🇦🇺</span>
          <span style={{ fontSize: '24px', fontWeight: 700, color: '#000000' }}>Built for Australian jobs (ANZSCO)</span>
        </div>
      </div>

      {/* URL */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#000000',
          border: '3px solid #000000',
          borderRadius: '8px',
          padding: '20px 40px',
        }}
      >
        <span style={{ fontSize: '28px', fontWeight: 700, color: '#ffffff' }}>
          ai-job-exposure.setiyaputra.me
        </span>
      </div>
    </div>,
    {
      width: 1080,
      height: 1080,
    }
  );

  const buffer = await response.arrayBuffer();
  writeFileSync('public/instagram-share.png', Buffer.from(buffer));
  console.log('Generated public/instagram-share.png');
}

generateInstagram();
