package handler

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
)

// ShortBatchItem describes a ready-to-confirm short-video highlight candidate.
type ShortBatchItem struct {
	ID            string   `json:"id"`
	Title         string   `json:"title"`
	SourceTitle   string   `json:"source_title"`
	SourceURL     string   `json:"source_url"`
	SourceChannel string   `json:"source_channel"`
	StartSec      int      `json:"start_sec"`
	EndSec        int      `json:"end_sec"`
	DurationSec   int      `json:"duration_sec"`
	Score         int      `json:"score"`
	Tags          []string `json:"tags"`
	Status        string   `json:"status"`
	Note          string   `json:"note"`
}

type ShortBatchConfirmRequest struct {
	Event      string         `json:"event"`
	Source     string         `json:"source"`
	Batch      []ShortBatchItem `json:"batch"`
	ConfirmedAt string        `json:"confirmed_at"`
}

type ShortBatchConfirmHandler struct{}

func NewShortsConfirmHandler() *ShortBatchConfirmHandler {
	return &ShortBatchConfirmHandler{}
}

func (h *ShortBatchConfirmHandler) RegisterRoutes(r *gin.Engine) {
	r.GET("/api/v1/shorts/default-batch", h.DefaultBatch)
	r.POST("/api/v1/shorts/confirm", h.Confirm)
}

func (h *ShortBatchConfirmHandler) DefaultBatch(c *gin.Context) {
	batch, err := h.loadDefaultBatch()
	if err != nil {
		InternalServerError(c, "加载默认批次失败: "+err.Error())
		return
	}

	SuccessWithMessage(c, map[string]interface{}{
		"status":      "ready",
		"authorized":  true,
		"batch_count": len(batch),
		"batch":       batch,
		"source":      "data/generated/default_batch.json",
	}, "默认短视频批次已准备好")
}

func (h *ShortBatchConfirmHandler) Confirm(c *gin.Context) {
	var req ShortBatchConfirmRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		BadRequest(c, "请求参数错误: "+err.Error())
		return
	}

	if req.Batch == nil || len(req.Batch) == 0 {
		batch, err := h.loadDefaultBatch()
		if err == nil {
			req.Batch = batch
		}
	}

	if req.Event == "" {
		req.Event = "default_short_batch_confirm"
	}
	if req.Source == "" {
		req.Source = "pages-default-batch"
	}
	if req.ConfirmedAt == "" {
		req.ConfirmedAt = time.Now().UTC().Format(time.RFC3339)
	}

	SuccessWithMessage(c, map[string]interface{}{
		"status":       "confirmed",
		"event":        req.Event,
		"source":       req.Source,
		"batch_count":  len(req.Batch),
		"confirmed_at": req.ConfirmedAt,
	}, "默认批次已确认，等待后台继续处理")
}

func (h *ShortBatchConfirmHandler) loadDefaultBatch() ([]ShortBatchItem, error) {
	paths := []string{
		filepath.Join(".", "data", "generated", "default_batch.json"),
		filepath.Join(".", "data", "highlights.json"),
	}

	for _, p := range paths {
		data, err := os.ReadFile(p)
		if err != nil {
			continue
		}

		var wrapper struct {
			Batch []ShortBatchItem `json:"batch"`
		}
		if err := json.Unmarshal(data, &wrapper); err == nil && len(wrapper.Batch) > 0 {
			return wrapper.Batch, nil
		}

		var items []ShortBatchItem
		if err := json.Unmarshal(data, &items); err == nil && len(items) > 0 {
			return items, nil
		}
	}

	return nil, fmt.Errorf("default batch data not found")
}
