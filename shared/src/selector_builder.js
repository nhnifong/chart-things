// Starting at clicked element, walk tree towards root,
// building selector, until selector selects only one thing.
// percent are used in this file for python to substitute values
const getCssSelectorShort = (elem) => {
  let el = elem;
  let path = [], parent;
  let selector = '';
  while (parent = el.parentNode) {
    let tag = el.tagName, siblings;
    path.unshift(
      (%i && el.id) ? `#${el.id}` : (
        siblings = parent.children,
        [].filter.call(siblings, sibling => sibling.tagName === tag).length === 1 ? tag :
        `${tag}:nth-child(${1+[].indexOf.call(siblings, el)})`
      )
    );
    el = parent;

    // Test it
    selector = `${path.join(' > ')}`.toLowerCase();
    const matches = document.querySelectorAll(selector);
    if (matches.length === 1 && matches[0] === elem) {
    	break;
    }
  };
  return selector;
};
return getCssSelectorShort(document.elementFromPoint(%i, %i));