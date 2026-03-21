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
        backgroundColor: '#0f172a',
        fontFamily: 'system-ui, sans-serif',
        padding: '60px',
        justifyContent: 'space-between',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <h1
          style={{
            fontSize: '72px',
            fontWeight: 800,
            color: '#ffffff',
            margin: 0,
            letterSpacing: '-2px',
          }}
        >
          Surya Setiyaputra
        </h1>
        <p
          style={{
            fontSize: '32px',
            fontWeight: 500,
            color: '#94a3b8',
            margin: '15px 0 0 0',
          }}
        >
          Software Engineer in Sydney, Australia
        </p>
      </div>

      {/* Tags */}
      <div
        style={{
          display: 'flex',
          gap: '15px',
          flexWrap: 'wrap',
        }}
      >
        <span
          style={{
            backgroundColor: '#3b82f6',
            color: '#ffffff',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          AI Agent Engineering
        </span>
        <span
          style={{
            backgroundColor: '#10b981',
            color: '#ffffff',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          Open Source
        </span>
        <span
          style={{
            backgroundColor: '#f59e0b',
            color: '#000000',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          Civic Tech
        </span>
        <span
          style={{
            backgroundColor: '#ec4899',
            color: '#ffffff',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          Side Projects
        </span>
      </div>

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: '28px', fontWeight: 700, color: '#ffffff' }}>
          setiyaputra.me
        </span>
        <div
          style={{
            display: 'flex',
            gap: '20px',
          }}
        >
          <span style={{ fontSize: '20px', color: '#94a3b8' }}>TypeScript</span>
          <span style={{ fontSize: '20px', color: '#94a3b8' }}>Python</span>
          <span style={{ fontSize: '20px', color: '#94a3b8' }}>Cloudflare</span>
          <span style={{ fontSize: '20px', color: '#94a3b8' }}>Multi-Agent AI</span>
        </div>
      </div>
    </div>,
    {
      width: 1200,
      height: 630,
    }
  );

  const buffer = await response.arrayBuffer();
  writeFileSync('/home/polybot/projects/hugo-static/public/og-image.png', Buffer.from(buffer));
  console.log('Generated og-image.png');
}

generate();
