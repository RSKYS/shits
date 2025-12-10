(function() {
  const header = '# Netscape HTTP Cookie File\n\n';
  const domain = '.youtube.com';
  const path = '/';
  const secure = 'FALSE';
  const expiry = '0';
  let output = header;
  document.cookie.split(';').forEach(cookie => {
    cookie = cookie.trim();
    if (cookie) {
      const [name, ...valueParts] = cookie.split('=');
      const value = decodeURIComponent(valueParts.join('='));
      output += `${domain}\tTRUE\t${path}\t${secure}\t${expiry}\t${name}\t${value}\n`;
    }
  });
  const blob = new Blob([output], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cookies.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
})();
