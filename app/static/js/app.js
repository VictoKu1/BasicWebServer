'use strict';

(function () {
	// Utilities
	function $(selector) {
		return document.querySelector(selector);
	}
	function escapeHtml(text) {
		return String(text)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;');
	}
	function scrollCommentsToBottom() {
		const commentsSection = $('.comments-section');
		if (!commentsSection) return;
		commentsSection.scrollTop = commentsSection.scrollHeight;
	}
	// Random 5-char alphanumeric ID for default usernames
	function generateRandomId(len = 5) {
		const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
		let out = '';
		for (let i = 0; i < len; i++) {
			out += chars.charAt(Math.floor(Math.random() * chars.length));
		}
		return out;
	}

	document.addEventListener('DOMContentLoaded', function () {
		const textarea = $('#content');
		const charCount = $('#charCount');
		const submitBtn = $('#submitBtn');
		const commentsList = $('#commentsList');
		const settingsBtn = $('#settingsBtn');
		const settingsModal = $('#settingsModal');
		const settingsClose = $('#settingsClose');
		const settingsSave = $('#settingsSave');
		const usernameInput = $('#usernameInput');
		const bulkMsgInput = $('#bulkMessage');
		const bulkCountInput = $('#bulkCount');
		const bulkIntervalInput = $('#bulkInterval');
		const bulkStartBtn = $('#bulkStart');
		const bulkStopBtn = $('#bulkStop');
		let lastSignature = '';
		let bulkTimer = null;
		let bulkRemaining = 0;

		// Character counter
		if (textarea && charCount && submitBtn) {
			textarea.addEventListener('input', function () {
				const length = this.value.length;
				charCount.textContent = length;
				submitBtn.disabled = length === 0;
			});
		}

	// Username from localStorage (generate 5-char default if missing)
		try {
			let savedName = (localStorage.getItem('forumUsername') || '').trim();
			if (!savedName) {
			savedName = generateRandomId(5);
				localStorage.setItem('forumUsername', savedName);
			}
			if (usernameInput) usernameInput.value = savedName;
		} catch (_) {}

		// Scroll to bottom on load (and after layout)
		scrollCommentsToBottom();
		setTimeout(scrollCommentsToBottom, 0);
		setTimeout(scrollCommentsToBottom, 100);

		// Form submit validation
		const form = $('#commentForm');
		if (form && textarea) {
			form.addEventListener('submit', function (e) {
				let content = textarea.value.trim();
				// Ensure username is set; generate 5-char default if missing
				let uname = '';
				try {
					uname = (localStorage.getItem('forumUsername') || '').trim();
					if (!uname) {
						uname = generateRandomId(5);
						localStorage.setItem('forumUsername', uname);
						if (usernameInput) usernameInput.value = uname;
					}
				} catch (_) {}
				// Prefix username
				if (content) {
					textarea.value = `[${uname}] ${content}`;
				} else {
					e.preventDefault();
					alert('Please enter a comment before submitting.');
				}
			});
		}

		// Enter to submit, Shift+Enter newline
		if (textarea && form) {
			textarea.addEventListener('keydown', function (e) {
				const isEnter = e.key === 'Enter' || e.keyCode === 13;
				if (isEnter && !e.shiftKey) {
					const content = textarea.value.trim();
					if (!content) {
						e.preventDefault();
						return;
					}
					e.preventDefault();
					form.submit();
				}
			});
		}

		// Global keyboard: focus textarea and start typing (unless a modal/input is active)
		document.addEventListener('keydown', function (e) {
			if (!textarea || !charCount || !submitBtn) return;
			if (e.ctrlKey || e.metaKey || e.altKey) return;

			// Don't hijack when user is typing in an input/textarea/contenteditable
			const ae = document.activeElement;
			const tag = (ae && ae.tagName) ? ae.tagName.toLowerCase() : '';
			const isTypingField = tag === 'input' || tag === 'textarea' || (ae && ae.isContentEditable);
			if (isTypingField) return;

		 // If settings modal is visible, don't redirect keys to main textarea
			if (settingsModal) {
				const visible = settingsModal.style && settingsModal.style.display !== 'none';
				if (visible) return;
			}

			if (document.activeElement === textarea) return;
			const key = e.key;
			if (!key) return;
			const isChar = key.length === 1;
			const isSpace = key === ' ' || key === 'Spacebar';
			const isBackspace = key === 'Backspace';
			const isEnter = key === 'Enter';
			if (isChar || isSpace || isBackspace || isEnter) {
				textarea.focus();
				if (isChar || isSpace) {
					textarea.value += isSpace ? ' ' : key;
					charCount.textContent = textarea.value.length;
					submitBtn.disabled = textarea.value.trim().length === 0;
				}
				e.preventDefault();
			}
		});

		// Render comments
		function linkify(text) {
			const urlRe = /\bhttps?:\/\/[^\s]+/gi;
			let lastIndex = 0;
			let result = '';
			let match;
			while ((match = urlRe.exec(text)) !== null) {
				const url = match[0];
				result += escapeHtml(text.slice(lastIndex, match.index));
				const safeUrl = escapeHtml(url);
				result += '<a href="' + safeUrl + '" target="_blank" rel="noopener noreferrer">' + safeUrl + '</a>';
				lastIndex = match.index + url.length;
			}
			result += escapeHtml(text.slice(lastIndex));
			return result;
		}

		function renderComments(comments) {
			if (!commentsList) return;
			if (!comments || comments.length === 0) {
				commentsList.innerHTML = '<div class="no-comments"><p>No comments yet. Be the first to share your thoughts!</p></div>';
				return;
			}
			const parts = [];
			for (const c of comments) {
				const raw = String(c.content ?? '');
				// Extract optional [DisplayName] prefix
				let displayName = '';
				let body = raw;
				const m = raw.match(/^\s*\[([^\]]+)\]\s*(.*)$/);
				if (m) {
					displayName = m[1];
					body = m[2];
				}
				const content = linkify(body);
				const created = escapeHtml(c.created_at ?? '');
				let headerHtml = '';
				if (displayName) {
					headerHtml = '<div class="comment-header">' + escapeHtml(displayName) + '</div>';
				}
				parts.push(
					'<div class="comment">' +
						headerHtml +
						'<div class="comment-content">' + content + '</div>' +
						'<div class="comment-timestamp">Posted on ' + created + ' UTC</div>' +
					'</div>'
				);
			}
			commentsList.innerHTML = parts.join('');
			// Ensure view focuses latest messages
			const last = commentsList.lastElementChild;
			if (last && typeof last.scrollIntoView === 'function') {
				last.scrollIntoView({ block: 'end' });
			}
			requestAnimationFrame(scrollCommentsToBottom);
			setTimeout(scrollCommentsToBottom, 0);
		}

		// Poll comments
		async function pollComments() {
			try {
				const res = await fetch('/api/comments', { cache: 'no-store' });
				if (!res.ok) return;
				const data = await res.json();
				const sig = JSON.stringify(data.map(d => [d.id, d.content, d.created_at]));
				if (sig !== lastSignature) {
					lastSignature = sig;
					renderComments(data);
				}
			} catch (err) {
				// ignore transient errors
			}
		}

		setTimeout(pollComments, 500);
		setInterval(pollComments, 1500);

		// Ensure textarea is ready for next input
		if (textarea) textarea.focus();

		// Settings modal controls
		function openSettings() {
			if (settingsModal) {
				settingsModal.style.display = 'flex';
				// focus first field for immediate typing
				if (usernameInput) setTimeout(() => usernameInput.focus(), 0);
			}
		}
		function closeSettings() {
			if (settingsModal) settingsModal.style.display = 'none';
			// return focus to main textarea
			if (textarea) textarea.focus();
		}
		if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
		if (settingsClose) settingsClose.addEventListener('click', closeSettings);
		if (settingsModal) {
			settingsModal.addEventListener('click', function (e) {
				if (e.target === settingsModal) closeSettings();
			});
		}
		if (settingsSave && usernameInput) {
			settingsSave.addEventListener('click', function () {
				try {
					let val = (usernameInput.value || '').trim();
					if (!val) {
						val = generateRandomId(5);
						usernameInput.value = val;
					}
					localStorage.setItem('forumUsername', val);
				} catch (_) {}
				closeSettings();
			});
		}

		// Bulk sender
		function stopBulk() {
			if (bulkTimer) {
				clearTimeout(bulkTimer);
				bulkTimer = null;
			}
			bulkRemaining = 0;
		}
		async function sendOnce(text) {
			if (!form) return;
			const fd = new FormData();
			// include CSRF token if present
			const tokenInput = form.querySelector('input[name="csrf_token"]');
			if (tokenInput && tokenInput.value) fd.append('csrf_token', tokenInput.value);
			// prepend username if configured
			let compose = text;
			try {
				let uname = (localStorage.getItem('forumUsername') || '').trim();
				if (!uname) {
					uname = generateRandomId(5);
					localStorage.setItem('forumUsername', uname);
					if (usernameInput) usernameInput.value = uname;
				}
				compose = `[${uname}] ${compose}`;
			} catch (_) {}
			fd.append('content', compose);
			try {
				await fetch('/post', { method: 'POST', body: fd, credentials: 'same-origin' });
			} catch (_) {}
		}
		if (bulkStartBtn && bulkStopBtn && bulkMsgInput && bulkCountInput && bulkIntervalInput) {
			bulkStartBtn.addEventListener('click', function () {
				stopBulk();
				const text = (bulkMsgInput.value || '').trim();
				const count = Math.max(1, Math.min(500, parseInt(bulkCountInput.value || '1', 10) || 1));
				const interval = Math.max(100, parseInt(bulkIntervalInput.value || '1000', 10) || 1000);
				// ensure username exists (generate default if needed)
				try {
					let uname = (localStorage.getItem('forumUsername') || '').trim();
					if (!uname) {
						uname = generateRandomUsername();
						localStorage.setItem('forumUsername', uname);
						if (usernameInput) usernameInput.value = uname;
					}
				} catch(_) {}
				if (!text) return;
				bulkRemaining = count;
				const tick = async () => {
					if (bulkRemaining <= 0) {
						stopBulk();
						return;
					}
					await sendOnce(text);
					bulkRemaining -= 1;
					if (bulkRemaining > 0) {
						bulkTimer = setTimeout(tick, interval);
					} else {
						stopBulk();
					}
				};
				tick();
			});
			bulkStopBtn.addEventListener('click', stopBulk);
		}
	});
})();


