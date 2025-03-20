
/**
 * Modal functionality for Bootstrap 5
 */
// Функция для переключения видимости спойлеров
function toggleSpoiler(spoilerId) {
    const content = document.getElementById(spoilerId);
    if (content) {
        const isVisible = content.style.display !== 'none';
        content.style.display = isVisible ? 'none' : 'block';
        
        // Вращаем стрелку
        const arrow = content.previousElementSibling.querySelector('.spoiler-arrow');
        if (arrow) {
            arrow.style.transform = isVisible ? '' : 'rotate(90deg)';
        }
    }
}

// Функция для предпросмотра изображения с заданными размерами
function previewImageResize(imageUrl, width, height, container) {
    if (!imageUrl) return;
    
    // Создаем или находим контейнер для предпросмотра
    const previewContainer = container || document.getElementById('imagePreviewContainer');
    if (!previewContainer) return;
    
    // Очищаем контейнер
    previewContainer.innerHTML = '';
    previewContainer.style.display = 'block';
    
    // Устанавливаем стили для контейнера
    previewContainer.style.maxWidth = '100%';
    previewContainer.style.margin = '10px 0';
    previewContainer.style.border = '1px solid rgba(255, 255, 255, 0.2)';
    previewContainer.style.borderRadius = '5px';
    previewContainer.style.overflow = 'hidden';
    previewContainer.style.padding = '10px';
    previewContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
    
    // Заголовок
    const previewTitle = document.createElement('div');
    previewTitle.innerHTML = '<i class="fas fa-eye"></i> Предпросмотр изображения:';
    previewTitle.style.marginBottom = '10px';
    previewTitle.style.fontWeight = 'bold';
    previewTitle.style.color = '#ccc';
    previewContainer.appendChild(previewTitle);
    
    // Создаем изображение для предпросмотра
    const img = document.createElement('img');
    img.src = imageUrl;
    img.className = 'bbcode-img';
    img.alt = 'Предпросмотр';
    
    // Устанавливаем размеры, если они указаны
    if (width) img.style.width = `${width}px`;
    if (height) img.style.height = `${height}px`;
    
    // Если размеры не указаны, используем responsive поведение
    if (!width && !height) {
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
    }
    
    // Добавляем информацию о размерах
    const sizeInfo = document.createElement('div');
    sizeInfo.style.marginTop = '8px';
    sizeInfo.style.fontSize = '12px';
    sizeInfo.style.color = '#aaa';
    sizeInfo.innerHTML = width && height 
        ? `Размер: ${width}px × ${height}px` 
        : width 
            ? `Ширина: ${width}px` 
            : 'Автоматический размер';
    
    // Добавляем элементы в контейнер
    previewContainer.appendChild(img);
    previewContainer.appendChild(sizeInfo);
    
    // Обработчик ошибок при загрузке изображения
    img.onerror = function() {
        previewContainer.innerHTML = '<div style="color: #ff6b6b;"><i class="fas fa-exclamation-triangle"></i> Ошибка загрузки изображения. Проверьте URL.</div>';
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modals on the page
    const modalElements = document.querySelectorAll('.modal');
    
    modalElements.forEach(modalElement => {
        // Create Modal instances with explicit backdrop option
        const modalOptions = {
            backdrop: true,
            keyboard: true,
            focus: true
        };
        
        try {
            // Create the modal instance with explicit options
            const modal = new bootstrap.Modal(modalElement, modalOptions);
            
            // Store the modal instance in the element
            modalElement._modalInstance = modal;
            
            // Handle modal triggers
            const triggers = document.querySelectorAll(`[data-bs-toggle="modal"][data-bs-target="#${modalElement.id}"]`);
            triggers.forEach(trigger => {
                trigger.addEventListener('click', function() {
                    modal.show();
                });
            });
            
            // Close modal when clicking outside
            modalElement.addEventListener('click', function(e) {
                if (e.target === this) {
                    modal.hide();
                }
            });
            
            // Prevent clicks on modal content from bubbling to modal
            const modalContent = modalElement.querySelector('.modal-content');
            if (modalContent) {
                modalContent.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        } catch (error) {
            console.error(`Error initializing modal #${modalElement.id}:`, error);
        }
    });
    
    // Close button functionality
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modalElement = this.closest('.modal');
            if (modalElement && modalElement._modalInstance) {
                modalElement._modalInstance.hide();
            } else {
                // Fallback to bootstrap's API
                try {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                } catch (error) {
                    console.error('Error closing modal:', error);
                }
            }
        });
    });
    
    // Global function to show modals programmatically
    window.showModal = function(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            try {
                if (modalElement._modalInstance) {
                    modalElement._modalInstance.show();
                } else {
                    const modal = new bootstrap.Modal(modalElement, {
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    });
                    modal.show();
                }
            } catch (error) {
                console.error(`Error showing modal #${modalId}:`, error);
            }
        }
    };
});
