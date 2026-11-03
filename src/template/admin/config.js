// Настройки админки. Пустой SUPABASE_URL = демо-режим (данные хранятся в браузере).
window.CT_ADMIN = {
  SUPABASE_URL: 'https://roqmejclibyyjlnxshzu.supabase.co',        // https://xxxx.supabase.co  (проект "tourizm")
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvcW1lamNsaWJ5eWpsbnhzaHp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxMzQ5OTcsImV4cCI6MjEwMTcxMDk5N30.Y4FhKvSa8b515buVumv3UTzX6mLti1aEmbrL38Jnvuc',   // publishable / anon key — он публичный, защита идёт через RLS
  BUILD_WEBHOOK: '',       // n8n webhook, который запускает `node build.mjs` на сервере
  SITE_URL: 'https://centrvietnam.ru',
  BUCKET: 'ct-media'
};
