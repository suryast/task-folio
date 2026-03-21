import { ImageResponse } from '@takumi-rs/image-response';
import { writeFileSync } from 'fs';

async function generatePreview() {
  const response = new ImageResponse(
    <div
      style={{
        width: '1200px',
        height: '630px',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f0f8fc',
        fontFamily: 'system-ui, sans-serif',
        padding: '40px',
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
          padding: '30px 40px',
          boxShadow: '8px 8px 0px 0px #000000',
        }}
      >
        <h1
          style={{
            fontSize: '72px',
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
            fontSize: '28px',
            fontWeight: 600,
            color: '#000000',
            margin: '10px 0 0 0',
          }}
        >
          See which tasks AI will automate — with timeframes
        </p>
      </div>

      {/* Stats Row */}
      <div
        style={{
          display: 'flex',
          gap: '20px',
          marginTop: '30px',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#ffffff',
            border: '4px solid #000000',
            borderRadius: '10px',
            padding: '20px 30px',
            boxShadow: '6px 6px 0px 0px #000000',
            flex: 1,
          }}
        >
          <span style={{ fontSize: '48px', fontWeight: 800, color: '#000000' }}>361</span>
          <span style={{ fontSize: '18px', fontWeight: 600, color: '#000000', opacity: 0.7 }}>OCCUPATIONS</span>
        </div>
        
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#ffffff',
            border: '4px solid #000000',
            borderRadius: '10px',
            padding: '20px 30px',
            boxShadow: '6px 6px 0px 0px #000000',
            flex: 1,
          }}
        >
          <span style={{ fontSize: '48px', fontWeight: 800, color: '#000000' }}>6,690</span>
          <span style={{ fontSize: '18px', fontWeight: 600, color: '#000000', opacity: 0.7 }}>TASKS ANALYZED</span>
        </div>
        
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#ffffff',
            border: '4px solid #000000',
            borderRadius: '10px',
            padding: '20px 30px',
            boxShadow: '6px 6px 0px 0px #000000',
            flex: 1,
          }}
        >
          <span style={{ fontSize: '48px', fontWeight: 800, color: '#000000' }}>82%</span>
          <span style={{ fontSize: '18px', fontWeight: 600, color: '#000000', opacity: 0.7 }}>AVG EXPOSURE</span>
        </div>
      </div>

      {/* Badges Row */}
      <div
        style={{
          display: 'flex',
          gap: '15px',
          marginTop: '30px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#97ee88',
            border: '3px solid #000000',
            borderRadius: '9999px',
            padding: '10px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '18px', fontWeight: 700, color: '#000000' }}>Low Impact</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#fed170',
            border: '3px solid #000000',
            borderRadius: '9999px',
            padding: '10px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '18px', fontWeight: 700, color: '#000000' }}>Medium Impact</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#ee8888',
            border: '3px solid #000000',
            borderRadius: '9999px',
            padding: '10px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
          }}
        >
          <span style={{ fontSize: '18px', fontWeight: 700, color: '#000000' }}>High Impact</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#ffffff',
            border: '3px solid #000000',
            borderRadius: '9999px',
            padding: '10px 25px',
            boxShadow: '4px 4px 0px 0px #000000',
            marginLeft: 'auto',
          }}
        >
          <span style={{ fontSize: '18px', fontWeight: 700, color: '#000000' }}>🇦🇺 Australian Jobs</span>
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          marginTop: 'auto',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: '16px', fontWeight: 600, color: '#000000', opacity: 0.5 }}>
          Data: ABS + Anthropic Economic Index (1M conversations)
        </span>
        <span style={{ fontSize: '16px', fontWeight: 600, color: '#000000', opacity: 0.5 }}>
          taskfolio-au.pages.dev
        </span>
      </div>
    </div>,
    {
      width: 1200,
      height: 630,
      format: 'png',
    }
  );

  const buffer = await response.arrayBuffer();
  writeFileSync('public/preview.png', Buffer.from(buffer));
  console.log('Generated public/preview.png');
}

generatePreview();
