import { ImageResponse } from '@takumi-rs/image-response';
import { writeFileSync } from 'fs';

async function generate() {
  const response = new ImageResponse(
    <div
      style={{
        width: '1200px',
        height: '630px',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f0f8fc',
        fontFamily: 'system-ui, sans-serif',
        padding: '50px',
        justifyContent: 'space-between',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#88d4ee',
          border: '4px solid #000000',
          borderRadius: '10px',
          padding: '30px 40px',
          boxShadow: '8px 8px 0px 0px #000000',
        }}
      >
        <h1
          style={{
            fontSize: '48px',
            fontWeight: 800,
            color: '#000000',
            margin: 0,
            lineHeight: 1.2,
          }}
        >
          TaskFolio: Seeing Which Parts of Your Job AI Will Actually Affect
        </h1>
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
            padding: '20px 35px',
            boxShadow: '5px 5px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '42px', fontWeight: 800, color: '#000000' }}>361</span>
          <span style={{ fontSize: '16px', fontWeight: 600, color: '#000000' }}>OCCUPATIONS</span>
        </div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            backgroundColor: '#ffffff',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '20px 35px',
            boxShadow: '5px 5px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '42px', fontWeight: 800, color: '#000000' }}>6,690</span>
          <span style={{ fontSize: '16px', fontWeight: 600, color: '#000000' }}>TASKS</span>
        </div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            backgroundColor: '#ee8888',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '20px 35px',
            boxShadow: '5px 5px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '42px', fontWeight: 800, color: '#000000' }}>Half-Life</span>
          <span style={{ fontSize: '16px', fontWeight: 600, color: '#000000' }}>METRIC</span>
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
          }}
        >
          <span style={{ fontSize: '24px', fontWeight: 700, color: '#000000' }}>setiyaputra.me</span>
        </div>
        <div
          style={{
            display: 'flex',
            backgroundColor: '#97ee88',
            border: '3px solid #000000',
            borderRadius: '8px',
            padding: '15px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '20px', fontWeight: 700, color: '#000000' }}>Open Source - MIT License</span>
        </div>
      </div>
    </div>,
    {
      width: 1200,
      height: 630,
    }
  );

  const buffer = await response.arrayBuffer();
  writeFileSync('public/og-taskfolio.png', Buffer.from(buffer));
  console.log('Generated public/og-taskfolio.png');
}

generate();
