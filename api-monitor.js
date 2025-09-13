// Скрипт для мониторинга API запросов в реальном времени
console.log('[API-MONITOR] Загружаем монитор API запросов');

// Перехватываем все fetch запросы
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  const options = args[1] || {};
  
  console.log('[API-MONITOR] 🌐 Fetch запрос:', {
    url: url,
    method: options.method || 'GET',
    headers: options.headers,
    body: options.body
  });
  
  return originalFetch.apply(this, args)
    .then(response => {
      console.log('[API-MONITOR] ✅ Fetch ответ:', {
        url: url,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      // Клонируем ответ для чтения тела
      const clonedResponse = response.clone();
      clonedResponse.json().then(data => {
        console.log('[API-MONITOR] 📄 Тело ответа:', data);
      }).catch(e => {
        // Игнорируем ошибки парсинга JSON
      });
      
      return response;
    })
    .catch(error => {
      console.error('[API-MONITOR] ❌ Fetch ошибка:', {
        url: url,
        error: error.message
      });
      throw error;
    });
};

// Перехватываем XMLHttpRequest
const originalXHR = window.XMLHttpRequest;
window.XMLHttpRequest = function() {
  const xhr = new originalXHR();
  const originalOpen = xhr.open;
  const originalSend = xhr.send;
  
  xhr.open = function(method, url, ...args) {
    console.log('[API-MONITOR] 🌐 XHR запрос:', {
      method: method,
      url: url
    });
    
    return originalOpen.apply(this, [method, url, ...args]);
  };
  
  xhr.send = function(data) {
    console.log('[API-MONITOR] 📤 XHR отправка:', {
      url: xhr._url || 'unknown',
      data: data
    });
    
  xhr.addEventListener('load', function() {
    let responseText = '';
    try {
      if (xhr.responseType === '' || xhr.responseType === 'text') {
        responseText = xhr.responseText.substring(0, 200) + (xhr.responseText.length > 200 ? '...' : '');
      } else {
        responseText = `[${xhr.responseType}] ${xhr.response ? xhr.response.byteLength || xhr.response.length || 'unknown size' : 'no data'}`;
      }
    } catch (e) {
      responseText = '[unable to read response]';
    }
    
    console.log('[API-MONITOR] ✅ XHR ответ:', {
      url: xhr._url || 'unknown',
      status: xhr.status,
      statusText: xhr.statusText,
      responseText: responseText
    });
  });
    
    xhr.addEventListener('error', function() {
      console.error('[API-MONITOR] ❌ XHR ошибка:', {
        url: xhr._url || 'unknown',
        status: xhr.status,
        statusText: xhr.statusText
      });
    });
    
    return originalSend.apply(this, [data]);
  };
  
  return xhr;
};

// Мониторим Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', function(event) {
    console.log('[API-MONITOR] 📨 Service Worker сообщение:', event.data);
  });
}

// Мониторим WebSocket
const originalWebSocket = window.WebSocket;
window.WebSocket = function(url, protocols) {
  console.log('[API-MONITOR] 🔌 WebSocket подключение:', {
    url: url,
    protocols: protocols
  });
  
  const ws = new originalWebSocket(url, protocols);
  
  ws.addEventListener('open', function() {
    console.log('[API-MONITOR] ✅ WebSocket подключен:', url);
  });
  
  ws.addEventListener('message', function(event) {
    console.log('[API-MONITOR] 📨 WebSocket сообщение:', {
      url: url,
      data: event.data
    });
  });
  
  ws.addEventListener('error', function(error) {
    console.error('[API-MONITOR] ❌ WebSocket ошибка:', {
      url: url,
      error: error
    });
  });
  
  ws.addEventListener('close', function(event) {
    console.log('[API-MONITOR] 🔌 WebSocket закрыт:', {
      url: url,
      code: event.code,
      reason: event.reason
    });
  });
  
  return ws;
};

console.log('[API-MONITOR] Монитор API загружен. Все запросы будут логироваться в консоль');
