const img = document.querySelector("preview");
img.onclick = (e) => {
  const x = e.pageX - e.target.offsetLeft;
  const y = e.pageY - e.target.offsetTop;
  console.log('clicked '+x+' '+y);
  window.location.href = '/locate?x='+x+'&y='+y;
};